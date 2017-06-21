# Imports
import numpy as np
import string
from keras.preprocessing import sequence, text
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, LSTM
from keras.layers import Input, Embedding, Reshape
from keras.layers import Conv1D, Conv2D, MaxPooling1D
from keras.layers.merge import Concatenate
from keras.optimizers import Adam

# Hilfsfunktionen
# Gibt 'size' lange, zufällige kleingeschriebene Ascii-Zeichen als String zurück
def random_str(size):
    res = b""
    while len(res) < size:
        res+=np.random.choice(list(string.ascii_lowercase)).encode('utf-8')
    return res
# Gibt shape[0] Strings aus je shape[1] zufälligen kleingeschriebenen Ascii-Zeichen zurück
def random_str_array(shape):
    res = list()
    count = shape[0]
    size = shape[1]
    while len(res) < count:
        buf = b""
        while len(buf) < size:
            buf+=np.random.choice(list(string.ascii_lowercase)).encode('utf-8')
        res.append(buf)
    return res
def to_matrix(strlist):
    shape = (len(strlist), len(strlist[0]))
    out = np.zeros(shape=shape)
    for i_sent in range(shape[0]):
        for i_char in range(shape[1]):
            out[i_sent][i_char] = strlist[i_sent][i_char] / 255
    return out
def from_matrix(matrix):
    buf = np.rint(matrix.astype(dtype=np.uint8)*255)
    out = list()
    for sentence in buf:
        strbuf = ""
        for pos in sentence:
            strbuf += chr(pos)
    return out
            

# Messages generieren
np.random.seed(0x42)
n = 64
msg_bits = 8* n
key_bits = 8* n

msglist = random_str_array((100, n))
keylist = random_str_array((100, n))
msglist[0] = b"koalabaerenbande "
while len(msglist[0]) < n:
    msglist[0]+=np.random.choice(list(string.ascii_lowercase)).encode('utf-8')
msgs = to_matrix(msglist)
keys = to_matrix(keylist)

# Alice
def get_alice():
    al_msg_in = Input(shape=(n,))
    al_key_in = Input(shape=(n,))
    al_merge = Concatenate()([al_msg_in, al_key_in])
    al_hidden = Dense(2*n)(al_merge)
    al_hidden = Reshape((2*n, 1))(al_hidden)
    al_hidden = Conv1D(filters=n, kernel_size=n+1, activation='relu')(al_hidden)
    al_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(al_hidden)
    al_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(al_hidden)
    al_hidden = Conv1D(filters=n, kernel_size=n, activation='relu')(al_hidden)
    al_output = Reshape((n,))(al_hidden)
    alice = Model([al_msg_in, al_key_in], al_output)
    alice.compile(loss='mse', optimizer='adam')
    alice.summary()
    return alice

# Bob
def get_bob():
    bob_comm_in = Input(shape=(n,))
    bob_key_in = Input(shape=(n,))
    bob_merge = Concatenate()([bob_comm_in, bob_key_in])
    bob_hidden = Dense(2*n)(bob_merge)
    bob_hidden = Reshape((2*n, 1))(bob_hidden)
    bob_hidden = Conv1D(filters=n, kernel_size=n+1, activation='relu')(bob_hidden)
    bob_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(bob_hidden)
    bob_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(bob_hidden)
    bob_hidden = Conv1D(filters=n, kernel_size=n, activation='relu')(bob_hidden)
    bob_output = Reshape((n,))(bob_hidden)
    bob = Model([bob_comm_in, bob_key_in], bob_output)
    bob.compile(loss='mse', optimizer='adam')
    bob.summary()
    return bob


# Eve
def get_eve():
    eve_comm_in = Input(shape=(n,1))
    eve_hidden = Dense(2*n)(eve_comm_in)
    eve_hidden = Dense(2*n)(eve_hidden)
    eve_hidden = Conv1D(filters=n, kernel_size=10, padding='same', activation='relu')(eve_hidden)
    eve_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(eve_hidden)
    eve_hidden = Conv1D(filters=n, kernel_size=6, padding='same', activation='relu')(eve_hidden)
    eve_hidden = Conv1D(filters=n, kernel_size=n, activation='relu')(eve_hidden)
    eve_output = Reshape((n,))(eve_hidden)
    eve = Model(eve_comm_in, eve_output)
    eve.compile(loss='mse', optimizer='adam')
    eve.summary()
    return eve

# Program
alice = get_alice()
bob = get_bob()
eve = get_eve()


# Complete model
ab_msg_in = Input(shape=(n, ))
ab_key_in = Input(shape=(n, ))

ab_h = alice([ab_msg_in, ab_key_in])
ab_out = bob([ab_h, ab_key_in])

alice_bob = Model([ab_msg_in, ab_key_in], ab_out)
alice_bob.compile(loss='mse', optimizer='adam')
alice_bob.summary()

#
# Ausführungsschritte
#   1. MSG, KEY -> Comm@Alice
#   2. Comm, KEY -> MSG@Bob
#   3. Comm -> MSG@Eve
#
alice_bob.fit(x=[msgs, keys],
              y=msgs,
              batch_size=32,
              epochs=1,
              verbose=1)
