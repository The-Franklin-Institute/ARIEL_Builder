
frutiger = "Frutiger-Roman.ttf"
frutigerBold = "Frutiger-Bold.ttf"

many = ["BradleyHandITC.ttf","Chalkboard.ttf","Cracked.ttf","CurlzMT.ttf","Frutiger-Bold.ttf","Frutiger-Itlic.ttf","Frutiger-Roman.ttf","Harrington.ttf","LucidaHandwriting-Italic.ttf","Papyrus.ttf","PartyLetPlain.ttf","PortagoITCTT.ttf","SynchroLET.ttf"]

def getFont():
    import random
    global many
    return random.choice(many)


