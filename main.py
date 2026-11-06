import pygame

pygame.init()

window = pygame.display.set_mode((200,150))
window.fill((0,0,0))
pygame.display.set_caption("Coolest game OAT")

while True:
    #take input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit(0)
    window.fill((255,255,255))

    pygame.display.flip()