import os
from datetime import datetime
import PIL
import pyautogui
import time
from file_read_backwards import FileReadBackwards
import re
import pydirectinput
import keyboard

pyautogui.pause = 0

def stop_script():
    if keyboard.is_pressed("b"):
        print("stopping")
        quit()

def arena_get_line(func):
    stop_script()
    with FileReadBackwards(r"C:\Users\The Brick\AppData\LocalLow\Wizards Of The Coast\MTGA\player.log", encoding="utf-8") as arenalog:
        for logentry in arenalog:
            if len(logentry) < 200:
                continue
            if logentry.find("\"promptId\": ") == -1:
                continue
            tacos = 0 # <3 tacos (loop index)
            while tacos < len(logentry):
                CurPrompt = logentry.find("\"promptId\": ",tacos) + 12
                if CurPrompt == 11: #if logentry.find("\"promptId\": ",tacos) returns -1
                    break
                tacos = CurPrompt
                if func(re.sub('[^0-9]', '', logentry[CurPrompt:CurPrompt+6])) == True:
                    return True
            return False
    return False

def full_read(prompt):
    stop_script()
    time.sleep(1)
    print(prompt)  
    match prompt: #returns PromptID number
        case "2":   #action availible
            print("action availible")
            PlayAll()
            return False #may need to be true  
        case "6":   #declare attacker
            print("declare attackers")
            PressNext()
            time.sleep(.5)
            pyautogui.click((resx // 2), (resy // 10))
            return False
        case "7":   #declare blockers, but also this sometimes comes up in mainphase
            print("declare blockers")
            PressNext()
            return False
        case "9":   #order combat damage
            print("order combat damage")
            PressNext()
            return True
        case "11":  #cancel/pay spell cast
            print("cancel cast")
            PressUndo()
            return True
        case "27"|"29"|"30":  #end game?
            print("end game?")
            time.sleep(.5)
            for i in range(4):  #[UNTESTED]  click down bottom third slightly off center to skip game review prompts
                stop_script()   
                pyautogui.mouseDown(31 * (resx // 60), resy - (resy * (i + 4) // 60))
                time.sleep(.1)
                pyautogui.mouseUp()
            for i in range(10):  #second loop to skip the cancel button during que
                stop_script()
                pyautogui.mouseDown(31 * (resx // 60), resy - (resy * (i + 10) // 60))
                time.sleep(.1)
                pyautogui.mouseUp()
            time.sleep(0.5)
            pyautogui.mouseDown(resx-(resx // 10), resy-(resy // 13)) #original (1730, 100)
            time.sleep(0.01)
            pyautogui.mouseUp()
            time.sleep(.1)
            return True
        case "34":  #first mulligan/other mulligans
            print("first mulligan")
            PressNext()
            return True
        case "36":  #other mulligans/mid mulligan
            print("other mulligan")
            PressNext()
            return True
        case "37"|"1"|"23":  #idk #1 might be a quantity for sacrifice targets
            print("idk")
            print(prompt)
            return False
        case "8": #idk but it sometimes hangs on 8
            PressNext()
            return False
        case "92":  #scry during mulligan
            print("scry during mulligan")
            return False
        case "14"|"1024":  #discard card
            print("discard card") #might also trigger when milled
            Concede(prompt)
            return True
        case "1029": #sacrifice creature
            print("sacrifice a creature")
            print(prompt)
            Concede()
            return True
        case "112"|"4031"|"1217": #at least one of these is from the card [Long Reach of Night]
            print("long reach of night")
            print(prompt)
            Concede(prompt)
            return True
        case "4482": #[Veil of fear]
            print("Veil of Fear")
            Concede(prompt)
            return True
        case "10"|"5270": #opponent going to negative life with [Platnium Angle]? Also from casting [Soulhunter Rakshasa]
            print("platnum angle?")
            Concede(prompt)
            return True
        case "118": #Pick a color [Coldsteel Heart]
            print("picking a color")
            pyautogui.click((resx // 2),(21 * (resy // 32))) #picks green
            return False
        case "5014": #exploit
            print("exploit")
            Concede(prompt)
            return True
        case "72": #sacrifice duplicate legendary
            print("legend rule sacrifice")
            Concede(prompt)
            return True
        case "6988": #[Threats Undetected]
            print("Threats Undetected")
            Concede(prompt)
            return True
        case "9491": #[Tahsa, Unholy Archmage] (-2)
            print("Tasha, Unholy Archmage")
            Concede(prompt)
            return True
        case "1034": #[Mind Drain]
            print("Mind Drain")
            Concede(prompt)
            return True
        case "2218": #[Gutmorn, Pactbound Servant]
            print("Gutmorn, Pactbound Servant")
            Concede(prompt)
            return True
        case "2840": #search for snow land [Spirit of the Aldergard]
            print("search snow land")
            time.sleep(3.5)
            pyautogui.click((2 * (resx // 3)), (resy // 2))
            time.sleep(2)
            return False
        case "5293": #[Divine Gambit]
            print("Divine Gambit")
            PlayAll()
            return True
        case _:     #unknown promptIDs
            print("oh no")
            print(prompt)
            Concede("new_" + prompt) #when in doubt concede
            return False

def can_cast(prompt):
    stop_script()
    match prompt:
        case "2"|"5293":
            return True
        case "11":
            PressNext()
            return True
        case _:
            return False

def PlayAll():
    stop_script()
    a = resx // 5 #original was 393
    for x in range(13):
        pyautogui.click(a,(resy-(resy // 500))) #originally 1078
        pyautogui.moveTo(a,((resy // 3)), duration=.2)
        pyautogui.click()
        time.sleep(.08)
        pyautogui.click((5*(resx // 8)),(8*(resy // 10))) #click no on warning menu (nessecary for legend rule)
        time.sleep(.02 ) #aim for x<=.2
        if arena_get_line(can_cast) == False:
            return
        PressUndo()
        a += resx // 23 #original 84
    time.sleep(.2)
    PressNext()

def Concede(Id):
    stop_script()
    print("conceding")
    newpath = cpath + "\\" + Id #Going to save a screenshot of the game before conceding
    if not os.path.exists(newpath): #Check if folder for same Id exists. If not create it.
        os.makedirs(newpath)
    ClosingScreenshot = pyautogui.screenshot()
    ClosingScreenshot.save(newpath + "\\" + datetime.now().strftime("%d.%m.%Y_%H.%M.%S") + ".png")
    time.sleep(1)
    pyautogui.click((resx - (resx // 50)),(resy // 30))
    time.sleep(.5)
    pyautogui.mouseDown((resx // 2),(19 * (resy // 32)))
    time.sleep(0.5)
    pyautogui.mouseUp()
    time.sleep(5)

def PressUndo():
    stop_script()
    pydirectinput.press("z")

def PressNext():
    stop_script()
    pydirectinput.press("space")
    
print("ready")
time.sleep(3)
print("start")
global resx 
resx = 1920
global resy 
resy = 1080 # set screen resolution
global cpath  #prefered file location for concession screenshots
cpath = r'C:\Users\The Brick\Documents\MTGArenabot\concessions'
while True:
    stop_script()
    arena_get_line(full_read)

#   Run the code then press play in arena and it
#   should auto play.

#   Make sure to set your resolution above and set arena
#   to fullscreen. (idk if it will work in a different aspect ratio)

#   Avoid using cards that are module or target
#   or otherwise force you to make desicions

#   You can get banned for this. Current mitigation strategy is
#   avoid running for too long at a time.

#   fails to manditory blocks

#   Reached Diamond 1 in Historic During Brother's War in under 60 hours of playtime.

#Deck
#25 Forest
#4 Coldsteel Heart
#4 Overgrown Battlement
#3 Ghalta, Primal Hunger
#4 Steel Leaf Champion
#1 Colossal Majesty
#4 Gigantosaurus
#1 Goreclaw, Terror of Qal Sisma
#3 Rampaging Brontodon
#3 Rampart Smasher
#3 Garruk's Uprising
#1 Master Symmetrist
#4 Llanowar Greenwidow