import torch
import torch.nn.functional as F
words = open('/home/vlad/python/names.txt','r').read().splitlines() # we take all the names
chars = sorted(list(set(''.join(words)))) # forms the English alphabet

char = []

for j in chars: # I created the '.' + a-z line as it is a possible entry
    y = '.' + j
    char.append(y)

for i in chars: # I also created the rest (a-z + a-z) , total is 676 + 26 from earlier
    for j in chars:
        y = i + j
        char.append(y)

sto1 = {s:i+1 for i,s in enumerate(chars)}
sto1['.'] = 0 # start + end token


onetos = {i:s for s,i in sto1.items()} # reverse for creating output

stoi = {s:i+1 for i,s in enumerate(char)} # same as before
stoi['..'] = 0

itos = {i:s for s,i in stoi.items()}


a = torch.zeros((703,27),dtype = torch.int32)
x = 0

for w in words:
    chs = ['.'] + list(w) + ['.'] # same technique as bigrams but here we actually implement a different approach for zip to make it work
    x = len(chs)
    for str,chr in zip((chs[i] + chs[i+1] for i in range(x-1)) , chs[2:]): # we concatenate the first two chars of name to then add the third one => trigram!
        ix1 = stoi[str] # here we use the new special dictionary made for double letter string
        ix2 = sto1[chr] # subtle difference : here we use the same type of dictionary as for bigram since we need only ONE letter
        a[ix1,ix2] +=1

P = (a+1).float()

P /= P.sum(1,keepdim=True) # we normalise the values of each char apparition so that they sum to 1

g = torch.Generator().manual_seed(2147483647)

for i in range(10): # generating results
    out = []
    ix = 0
    prevch = '.' # we NEED the previous char to fetch it since without it it breaks. why? because it tries to find a row always in between
    # 0 and 27 as we have a 703x27 tensor!! not good! thats why we need prev char to associate correct values.
    while True:
        p = P[ix] # this is a row!!
        ix = torch.multinomial(p,num_samples=1,replacement=True,generator=g).item() # this is a value smaller than 27!!
        
        if ix == 0: # if it predicted that it goes to the first line which has . token as next first letter we stop
            break
    
        ch = onetos[ix] # we remember the char through its value
        out.append(ch)
        ix = stoi[prevch + ch] # we fetch the correct value as we use TWO chars
        prevch = ch

    #print(''.join(out))
        
for w in words[:3]:
    chs = ['.'] + list(w) + ['.']
    x = len(chs)
    for str,chr in zip((chs[i] + chs[i+1] for i in range(x-1)) , chs[2:]):
        ix1 = stoi[str]
        ix2 = sto1[chr]
        prob = P[ix1,ix2]
     #   print(f'{str,chr} : {prob:.4f}')

# verdict : a trigram is on average way more precise. samiyah sounds cool

xs , ys = [] , [] # xs is used for the first two characters, ys is for the third
for w in words:
    chs = ['.'] + list(w) + ['.']
    x = len(chs)
    for str,chr in zip((chs[i] + chs[i+1] for i in range(x-1)) , chs[2:]): 
        ix1 = stoi[str]
        ix2 = sto1[chr]
        xs.append(ix1) # memorising the values that represent the chars
        ys.append(ix2)

xs = torch.tensor(xs)
ys = torch.tensor(ys)

W = torch.randn( (703,27) , requires_grad=True )

for step in range(10^5): # training loop!
    result = W[xs]
    counts = result.exp()

    probability = counts / counts.sum(1,keepdim=True)

    loss = -probability[torch.arange(xs.size(0)),ys].log().mean() # NLL
    W.grad = None
    loss.backward()
    W.data += -100 * W.grad # gradient descent , niu = -100

for i in range(10):
    out = []
    ix = 0
    prevch = '.' 
    while True:
        logits = W[ix] # ix is bigram index
        counts = logits.exp()
        p = counts / counts.sum()

        ix = torch.multinomial(p,num_samples=1,replacement=True,generator=g).item()
        # here it becomes char index
        if ix == 0:
            break
    
        ch = onetos[ix] # we remember the char
        out.append(ch)
        ix = stoi[prevch + ch] # we fetch the correct value as we use TWO chars
        prevch = ch

    print(''.join(out)) # jam , jaridwine , uran , pean taley 
