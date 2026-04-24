import torch
import random
import torch.nn.functional as F

words = open('/home/vlad/python/names.txt','r').read().splitlines() # we take all the names
chars = sorted(list(set(''.join(words)))) # create the alphabet

stoi = {s:i+1 for i,s in enumerate(chars)}
stoi['.'] = 0

itos = {i:s for s,i in stoi.items()}

block_size = 3
number_of_embeddings = 10
neuron_number = 200
vocab_size = len(stoi)

def build_data(words):
    x , y = [] , [] # total 
    for w in words:
        context = [0] * block_size # we split in groups
        for ch in w + '.':
            ix = stoi[ch]
            x.append(context)
            y.append(ix)
            context = context[1:] + [ix]
    
    x = torch.tensor(x)
    y = torch.tensor(y)

    return x,y

random.seed(42)
random.shuffle(words) # we randomise

n1 = int(len(words)*0.8)
n2 = int(len(words)*0.9)
xtr , ytr = build_data(words[:n1]) # 80 - 10 - 10
xdev , ydev = build_data(words[n1:n2])
xt , yt = build_data(words[n2:])

class Linear: # first layer, just matrix mul + bias

    def __init__(self , fan_in , fan_out , bias = True):
        
        self.weight = torch.randn((fan_in,fan_out)) * (5/3)/fan_in**0.5 #kaiming init
        self.bias = torch.zeros(fan_out)

    def __call__(self , x):
        
        self.out = x @ self.weight
        
        if self.bias is not None:
            self.out += self.bias
        
        return self.out 
    
    def parameters(self):
        return [self.weight] + ([] if self.bias is None else [self.bias])
    
class BatchNorm1d: # batch normalisation

    def __init__(self , dim , eps = 1e-5 , momentum = 0.1):
        
        self.eps = eps # for batch norm
        self.momentum = momentum
        self.training = True # if trained later

        self.gamma = torch.ones(dim) # scale
        self.beta = torch.zeros(dim) # shift

        self.running_mean = torch.zeros(dim) # global estimate for example testing later
        self.running_var = torch.ones(dim) 

    def __call__(self, x):
        
        if self.training: # if its training and we have new batch
            xmean = x.mean(0,keepdim=True)
            xvar = x.var(0,keepdim=True)

        else:
            xmean = self.running_mean # not training , use global
            xvar = self.running_var

        xhat = (x - xmean) / torch.sqrt(xvar + self.eps) # formula
        self.out = self.gamma * xhat + self.beta

        if self.training:
            with torch.no_grad(): # calculated with exponential moving avg
                self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * xmean
                self.running_var = (1 - self.momentum) * self.running_var + self.momentum * xvar
        
        return self.out    

    def parameters(self):
        return [self.gamma,self.beta]
     
class Tanh: # simple tanh layer
    
    def __call__(self, x):
        
        self.out = torch.tanh(x)
        return self.out
    
    def parameters(self):
        return []

class Embedding: # attribute embeddings accordingly ; cleaner code
    
    def __init__(self , num_emb , emb_dim):
        self.weight = torch.randn((num_emb , emb_dim))
        
    def __call__(self , indexes):
        
        self.out = self.weight[indexes]
        return self.out
    
    def parameters(self):
        return [self.weight]

class Flatten: # flatten so we can broadcast

    def __call__(self, x):
       
        self.out = x.view(x.shape[0],-1)
        return self.out
    
    def parameters(self):
        return []

class Sequential: # do it in order so we dont have the order exposed

    def __init__(self,layers):
        self.layers = layers
    
    def __call__(self, x):
        
        for layer in self.layers:
            x = layer(x)
        
        self.out = x
        return self.out

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
    

model = Sequential([Embedding(vocab_size,number_of_embeddings) ,
          Flatten() ,
          Linear(number_of_embeddings * block_size , neuron_number , bias=False) , # we give the neural net a comprimed vector of all inputs so that we can avoid using tokens for now, better than bigram and trigram 
          BatchNorm1d(neuron_number) ,
          Tanh() ,
          Linear(neuron_number , vocab_size)])

with torch.no_grad():
    model.layers[-1].weight *= 0.1

parameters = model.parameters()

for p in parameters:
    p.requires_grad = True

max_steps = 175000
batch_size = 32

for i in range(max_steps):
    
    ix = torch.randint(0 , xtr.shape[0] , (batch_size, )) # pick batch_size values from 0 to max randomly
    xsample , ysample = xtr[ix] , ytr[ix] # truncate

    logits = model(xsample) # run it through the mlp
    
    loss = F.cross_entropy(logits,ysample) # compute loss

    for p in parameters: # avoid residue gradients
        p.grad = None
    
    loss.backward() # compute back propagation

    lr = 0.1 if i < 150000 else 0.01 # adjust lr
    
    for p in parameters:
        p.data += -lr * p.grad
    
for layer in model.layers:
    layer.training = False

@torch.no_grad()
def split_loss(split):
    
    a , b = {'train' :  (xtr,ytr) , 'val' :  (xdev,ydev) , 'test' : (xt,yt)}[split] # special syntax, creates dictionary
    
    t = model(a)
    
    loss = F.cross_entropy(t,b)
    
    print(split,loss.item())

split_loss('train')
split_loss('val')


for _ in range(20):
# sampling names
    contor = 0
    out = []
    context = [0] * block_size
    while True:
        contor +=1
        a = torch.tensor([context]) # a "batch" of size 1 since its 1 name , then we have block size and number of embeddings
        a = model(a) # run it through the layers sequentially

        logits = a
        probs = F.softmax(logits,dim=1) # e^x everything , then normalises by row
        ix = torch.multinomial(probs,num_samples=1).item()

        if ix == 0 or contor >=10:
            break

        context = context[1:] + [ix]
        out.append(ix)
    
    print(''.join(itos[i] for i in out))
