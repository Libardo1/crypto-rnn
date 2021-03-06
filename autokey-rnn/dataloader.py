# Decoding the Autokey Cipher with Recurrent Neural Networks
# Sam Greydanus. January 2017. MIT License.

import copy
import numpy as np

class Dataloader():
    def __init__(self, alphabet, tsteps, max_key_len):
        self.A = alphabet
        self.tsteps = tsteps
        self.max_key_len = max_key_len
    
    def encode(self, key, plain):
        cipher = '' ; key = copy.deepcopy(key)
        for i in range(len(plain)):
            plain_ix = self.A.find(plain[i])
            shift = self.A.find(key[i])
            assert plain_ix >=0, 'plaintext characters must exist in alphabet'
            assert shift >=0, 'key characters must exist in alphabet'
            cipher_ix = (plain_ix + shift) % len(self.A)
            cipher += self.A[cipher_ix]
            key += self.A[plain_ix] # for autokey, keyshifts are determined by appending plaintext to keyword
        return cipher
            
    def decode(self, key, cipher):
        plain = '' ; key = copy.deepcopy(key)
        for i in range(len(cipher)):
            cipher_ix = self.A.find(cipher[i])
            shift = self.A.find(key[i])
            assert cipher_ix >=0, 'ciphertext characters must exist in alphabet'
            assert shift >=0, 'key characters must exist in alphabet'
            plain_ix = (cipher_ix - shift) % len(self.A)
            plain += self.A[plain_ix]
            key += self.A[plain_ix] # for autokey, keyshifts are determined by appending plaintext to keyword
        return plain
    
    def rands(self, size):
        ix = np.random.randint(len(self.A),size=size)
        return ''.join([self.A[i] for i in ix])
    
    def one_hot(self, s):
        _A = copy.deepcopy(self.A) + '-'
        ix = [_A.find(l) for l in s]
        z = np.zeros((len(s),len(_A)))
        z[range(len(s)),ix] = 1
        return z
    
    def next_batch(self, batch_size, verbose=False):
        batch_X = [] ; batch_y = [] ; batch_Xs = [] ; batch_ks = [] ; batch_ys = []
        for _ in range(batch_size):
            ys = self.rands(self.tsteps)
            ks = self.rands(np.random.randint(self.max_key_len-1) + 1)
            # print(ks, self.A[:1])
            if ks is (self.A[:self.max_key_len]): # lets us check for overfitting later #self.key_len
                ks_ = ks
                ks = self.rands(np.random.randint(self.max_key_len-1) + 1)
                # print('conflict! key was "{}" but now is "{}"'.format(ks_, ks))
            Xs = self.encode(ks, ys)
            ks += '-'*(self.max_key_len - len(ks))
            if verbose: print(Xs, ks, ys)
            X = self.one_hot(ks + Xs)
            y = self.one_hot(ks + ys)
            batch_X.append(X)
            batch_y.append(y)
            batch_Xs.append(Xs) ; batch_ks.append(ks) ; batch_ys.append(ys)
        
        if not verbose:
            return (batch_X,batch_y)
        else:
            return (batch_X, batch_y, batch_Xs, batch_ks, batch_ys)