import random


class Game:
    tick_ms = 35
    def __init__(self, canvas, width, height):
        self.canvas, self.width, self.height = canvas, width, height
        self.score, self.keys = 0, set()
    def key(self, key, down): self.keys.discard(key) if not down else self.keys.add(key)
    def draw_score(self):
        self.canvas.delete("score")
        self.canvas.create_text(self.width-12, 15, anchor="e", text=str(self.score), fill="#d7e1ee", font=("Consolas", 12, "bold"), tags="score")
    def reset(self): self.__init__(self.canvas, self.width, self.height)


class Snake(Game):
    tick_ms = 155
    def __init__(self, *args):
        super().__init__(*args); self.cell=18; self.snake=[(10, 10),(9,10),(8,10)]; self.direction=(1,0); self.pending=self.direction; self.food=self._food()
    def _food(self):
        choices=[(x,y) for x in range(self.width//self.cell) for y in range(2,self.height//self.cell) if (x,y) not in self.snake]
        return random.choice(choices)
    def update(self):
        maps={"w":(0,-1),"up":(0,-1),"s":(0,1),"down":(0,1),"a":(-1,0),"left":(-1,0),"d":(1,0),"right":(1,0)}
        for key, direction in maps.items():
            if key in self.keys and direction != (-self.direction[0],-self.direction[1]): self.pending=direction
        self.direction=self.pending; x,y=self.snake[0]; nx=(x+self.direction[0])%(self.width//self.cell); ny=2+(y-2+self.direction[1])%((self.height//self.cell)-2); head=(nx,ny)
        if head in self.snake[:-1]: self.reset(); return
        self.snake.insert(0,head)
        if head==self.food: self.score+=1; self.food=self._food()
        else: self.snake.pop()
    def draw(self):
        self.canvas.delete("game"); c=self.cell
        for i,(x,y) in enumerate(self.snake): self.canvas.create_rectangle(x*c+2,y*c+2,(x+1)*c-2,(y+1)*c-2, fill="#e8f0ff" if i==0 else "#8796aa", outline="", tags="game")
        x,y=self.food; self.canvas.create_oval(x*c+4,y*c+4,(x+1)*c-4,(y+1)*c-4,fill="#ff6767",outline="",tags="game"); self.draw_score()


class Dodge(Game):
    def __init__(self,*args):
        super().__init__(*args); self.x=self.width/2; self.blocks=[]; self.age=0
    def update(self):
        self.age+=1; self.score=int(self.age/30*10)/10; self.x=max(12,min(self.width-12,self.x+(('d'in self.keys or 'right'in self.keys)-('a'in self.keys or 'left'in self.keys))*8))
        if self.age%18==0: self.blocks.append([random.randint(8,self.width-24),35,random.randint(4,8)])
        for b in self.blocks: b[1]+=b[2]
        self.blocks=[b for b in self.blocks if b[1]<self.height+20]
        if any(abs(b[0]-self.x)<18 and b[1]>self.height-45 for b in self.blocks): self.reset()
    def draw(self):
        self.canvas.delete("game"); self.canvas.create_oval(self.x-11,self.height-35,self.x+11,self.height-13,fill="#77e0b0",outline="",tags="game")
        for x,y,_ in self.blocks:self.canvas.create_rectangle(x,y,x+18,y+18,fill="#ff6b6b",outline="",tags="game")
        self.draw_score()


class Aim(Game):
    def __init__(self,*args): super().__init__(*args); self.target=None; self.new_target()
    def new_target(self): self.target=(random.randint(24,self.width-24),random.randint(45,self.height-24),random.randint(10,18))
    def click(self,event):
        x,y,r=self.target
        if (event.x-x)**2+(event.y-y)**2<=r*r: self.score+=1; self.new_target()
    def update(self): pass
    def draw(self):
        self.canvas.delete("game"); x,y,r=self.target
        self.canvas.create_oval(x-r,y-r,x+r,y+r,fill="#ff6767",outline="#fff",tags="game"); self.canvas.create_oval(x-3,y-3,x+3,y+3,fill="#fff",outline="",tags="game"); self.draw_score()


class Breakout(Game):
    def __init__(self,*args):
        super().__init__(*args); self.paddle=self.width/2; self.ball=[self.width/2,self.height-65,4,-4]; self.bricks=[(12+c*42,38+r*20) for r in range(4) for c in range(8)]
    def update(self):
        self.paddle=max(35,min(self.width-35,self.paddle+(('d'in self.keys or 'right'in self.keys)-('a'in self.keys or 'left'in self.keys))*9)); b=self.ball; b[0]+=b[2]; b[1]+=b[3]
        if b[0]<6 or b[0]>self.width-6:b[2]*=-1
        if b[1]<25:b[3]*=-1
        if b[1]>self.height:self.reset();return
        if b[3]>0 and self.height-42<b[1]<self.height-25 and abs(b[0]-self.paddle)<42:b[3]=-abs(b[3])
        for brick in self.bricks[:]:
            if brick[0]<b[0]<brick[0]+36 and brick[1]<b[1]<brick[1]+14:self.bricks.remove(brick);b[3]*=-1;self.score+=1;break
        if not self.bricks:self.reset()
    def draw(self):
        self.canvas.delete("game");
        for x,y in self.bricks:self.canvas.create_rectangle(x,y,x+36,y+14,fill="#819cff",outline="",tags="game")
        x,y,_,_=self.ball;self.canvas.create_oval(x-5,y-5,x+5,y+5,fill="#fff",outline="",tags="game");self.canvas.create_rectangle(self.paddle-35,self.height-28,self.paddle+35,self.height-20,fill="#77e0b0",outline="",tags="game");self.draw_score()


class Pong(Game):
    def __init__(self,*args): super().__init__(*args);self.player=self.height/2;self.cpu=self.height/2;self.ball=[self.width/2,self.height/2,4,3]
    def update(self):
        self.player=max(45,min(self.height-28,self.player+(('s'in self.keys or 'down'in self.keys)-('w'in self.keys or 'up'in self.keys))*7)); b=self.ball;b[0]+=b[2];b[1]+=b[3];self.cpu+=(b[1]-self.cpu)*.08
        if b[1]<30 or b[1]>self.height-5:b[3]*=-1
        if b[0]>self.width-25 and abs(b[1]-self.player)<35:b[2]=-abs(b[2])
        if b[0]<25 and abs(b[1]-self.cpu)<35:b[2]=abs(b[2]);self.score+=1
        if b[0]<0 or b[0]>self.width:self.reset()
    def draw(self):
        self.canvas.delete("game");b=self.ball;self.canvas.create_rectangle(self.width-18,self.player-28,self.width-10,self.player+28,fill="#77e0b0",outline="",tags="game");self.canvas.create_rectangle(10,self.cpu-28,18,self.cpu+28,fill="#9aa7b8",outline="",tags="game");self.canvas.create_oval(b[0]-5,b[1]-5,b[0]+5,b[1]+5,fill="#fff",outline="",tags="game");self.draw_score()
