
import pygame
import pygame.mixer

pygame.init()
pygame.mixer.init()

s = pygame.mixer.Sound('pyrpg/resources/sounds/spell3.wav')

pygame.mixer.Sound.play(s)