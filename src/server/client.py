from time import time


class Client:
    def __init__(self):
        self.__last_access_time = time()

    
    @property
    def last_access_time(self) -> float:
        return self.__last_access_time
    

    @last_access_time.setter
    def last_access_time(self, value):
        self.__last_access_time = value