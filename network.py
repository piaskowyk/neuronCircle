from PIL import Image, ImageDraw
import operator
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import random as random

class Network(object):

    size = 200
    howImage = 100
    limit = 0
    n = 0.01
    precission = 0.1
    maxTour = 200
    weight = np.zeros((size, size))
    value = np.zeros((size, size))
    lastValue = np.zeros(size)
    path = "./data"
    files = 0

    def __init__(self):
        self.files = [f for f in listdir(self.path) if isfile(join(self.path, f))]

##########################################################################################################

    def getDif(self, x:int, y:int, tmpX:int, tmpY:int, pixels):
        return abs(pixels[tmpX, tmpY][0] - pixels[x, y][0] + pixels[tmpX, tmpY][1] - pixels[x, y][1] + pixels[tmpX, tmpY][2] - pixels[x, y][2] + pixels[tmpX, tmpY][3] - pixels[x, y][3])

    def getValueNeuron(self, x:int, y:int, pixels):
        out = 0
        if(x - 1 >= 0 and y - 1 >= 0): 
            out += self.getDif(x, y, x - 1, y - 1, pixels)
        if(y - 1 >= 0): 
            out += self.getDif(x, y, x, y - 1, pixels)
        if(x + 1 < self.size and y - 1 >= 0): 
            out += self.getDif(x, y, x + 1, y - 1, pixels)
        if(x + 1 < self.size): 
            out += self.getDif(x, y, x + 1, y, pixels)
        if(x + 1 < self.size and y - 1 >= 0): 
            out += self.getDif(x, y, x + 1, y - 1, pixels)
        if(y + 1 < self.size): 
            out += self.getDif(x, y, x, y + 1, pixels)
        if(x - 1 >= 0 and y + 1 < self.size): 
            out += self.getDif(x, y, x - 1, y + 1, pixels)
        if(x - 1 >= 0): 
            out += self.getDif(x, y, x - 1, y, pixels)
        return out / (255+255+255)

    def network(self, pixels):
        networkSum = 0
        isBig = False
        for x in range(0, self.size):
            for y in range(0, self.size):
                self.value[x, y] = float(self.getValueNeuron(x, y, pixels))
                networkSum += float(self.value[x, y] * self.weight[x, y])
                if(networkSum > 100000):
                    networkSum /= 10
                    isBig = True
        if isBig: self.compressWeight()
        return networkSum

    def countNewWeight(self, networkSum):
        for x in range(0, self.size):
            for y in range(0, self.size):
                self.weight[x, y] += float(self.n * ( self.limit - networkSum ) * self.value[x, y])

    def randWeight(self):
        for x in range(0, self.size):
            for y in range(0, self.size):
                self.weight[x,y] = random.uniform(-1, 1)

    def compressWeight(self):
        isBig = False
        for x in range(0, self.size):
            for y in range(0, self.size):
                if(abs(self.weight[x,y]) > 100): 
                    isBig = True
                    break
            if isBig: break
        if isBig:
            for x in range(0, self.size):
                for y in range(0, self.size):
                    self.weight[x,y] /= 10

    def teachNetwork(self):
        index = 1
        for f in self.files:
            print(str(index) + "/" + str(self.howImage))
            index += 1
            img = Image.open("./data/"+f)
            pixels = img.load() 
            if(f.find('true') >= 0):
                print(f + " - search true")
                networkSum = self.network(pixels)
                print(networkSum)
                lastSum = networkSum
                tour = 0
                while networkSum < self.limit:
                    self.countNewWeight(networkSum)
                    self.compressWeight()
                    networkSum = self.network(pixels)
                    if(abs(networkSum - self.limit) < self.precission and abs(lastSum - networkSum) < self.precission): break
                    if(tour > self.maxTour): break
                    tour += 1
                    lastSum = networkSum
                    print(networkSum)
            else:
                print(f + " - search false")
                networkSum = self.network(pixels)
                print(networkSum)
                lastSum = networkSum
                tour = 0
                while networkSum > self.limit:
                    self.countNewWeight(networkSum)
                    networkSum = self.network(pixels)
                    if(abs(networkSum - self.limit) < self.precission and abs(lastSum - networkSum) < self.precission): break
                    if(tour > self.maxTour): break
                    tour += 1
                    lastSum = networkSum
                    print(networkSum)
            print('-----------------------------')
            self.saveWeightToFile()

    def loadWeightFromFile(self):
        weightFile = open('weight.txt', 'r')
        for line in weightFile:
            tmpline = line.split(':')
            weightItem = tmpline[1]
            tpmline2 = tmpline[0].split(',')
            self.weight[int(tpmline2[0]), int(tpmline2[1])] = float(weightItem)
    
    def saveWeightToFile(self):
        try:
            os.remove('weight.txt')
        except OSError:
            pass
        toSave = open('weight.txt', 'a')
        for x in range(0, self.size):
            for y in range(0, self.size):
                toSave.write(str(x) + ',' + str(y) + ':' + str(self.weight[x, y]) + '\n')
        toSave.close()

##########################################################################################################

    def randColor(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)

    def makeTrueImage(self, index):
        d = random.randint(10, 100)
        image = Image.new('RGBA', (self.size, self.size), self.randColor())
        if(random.randint(0, 10) % 3 == 0):
            pixels = image.load()
            for x in range(0, self.size):
                for y in range(0, self.size):
                    pixels[x,y] = self.randColor()
        x = random.randint(0, self.size - d)
        y = random.randint(0, self.size - d)
        x1 = x + d
        y1 = y + d
        draw = ImageDraw.Draw(image)
        draw.ellipse((x,y,x1,y1), fill = self.randColor())
        image.save('data/' + str(index) + 'true.png')

    def makeFalseImage(self, index):
        image = Image.new('RGBA', (self.size, self.size), self.randColor())
        pixels = image.load()
        if(random.randint(1, 2) % 2 == 0):
            for i in range(1, int(self.size * self.size / random.randint(1, 10))):
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                pixels[x,y] = self.randColor()
        else:
            for x in range(0, self.size):
                for y in range(0, self.size):
                    pixels[x,y] = self.randColor()
        image.save('data/' + str(index) + 'false.png')
    
    def generateImage(self):
        for i in range(0, self.howImage):
            if random.randint(1, 10) % 4 == 0:
                self.makeFalseImage(i)
            else:
                self.makeTrueImage(i)
            print(str(i) + "/" + str(self.howImage))

##########################################################################################################

    def check(self, pixels):
        networkSum = self.network(pixels)
        if(networkSum >= self.limit - self.precission):
            return True, networkSum
        else:
            return False, networkSum

    def testNetwork(self):
        count = 0
        good = 0
        tVal = 0
        fVal = 0
        for f in self.files:
            img = Image.open("./data/"+f)
            pixels = img.load() 

            net = self.check(pixels) 
            networkSum = net[1]           
            if(net[0]): 
                isCircle = True
                tVal += 1
            else: 
                isCircle = False
                fVal += 1

            print("Network say: " + f + " - " + str(isCircle) + " with value: " + str(networkSum))
            if(f.find('true') >= 0 and isCircle): good += 1
            if(f.find('false') >= 0 and not isCircle): good += 1
            count += 1

            print("-----------------------------------")

        print("All:" + str(count))
        print("Good:" + str(good))
        print("Ratio:" + str(good / count))
        print("True:" + str(tVal))
        print("False:" + str(fVal))