import requests
import os



# Wit speech API endpoint
API_ENDPOINT = 'https://api.wit.ai/speech'

# Audio path
AUDIO_PATH = "./audio.mp3"

# Wit.ai api access token
WIT_ACCESS_TOKEN = "YOUR_WIT_API_TOKEN"

async def solve(page):
    print_message("Solucionando Recaptcha",'\033[92m')
    try: 
        while True:
            frames = await recaptcha_click(page)
            if await check_green_mark(frames):
                print_log(" - Recaptcha checkbox já foi solucionado!")
                break
            else:       
                frames = page.frames   
                for frame in frames:            
                    if frame.url.find('api2/bframe') != -1 or await frame.is_visible("#recaptcha-audio-button"):
                        print_log(" - Frame de imagens encontrado!")
                        try:
                            # Click on the audio button in footer of the image frame
                            print_log(" - Procurando botão de audio...")
                            await recaptcha_audio_button(frame)
                            # Solve the audio challenge
                            print_log(" - Procurando frame de audio...")
                            await challenge_solver(frame) 
                            await page.wait_for_timeout(500)                
                            if await frame.is_visible(".rc-doscaptcha-header-text"):
                                if await frame.inner_text(".rc-doscaptcha-header-text") == "Try again later":
                                    raise Exception("Recaptcha bloqueou testes por audio. Tente mais tarde!")
                            elif await frame.is_disabled('#recaptcha-verify-button'):
                                print_log(" - Botão de verificação do recaptcha foi desabilitado!")
                                print_message("Recaptcha solucionado!",'\033[92m')
                                return False
                        except Exception as error:
                            if frame.is_detached():
                                print_log(" - Frame de audio foi desconectado antes da verificação!")
                                print_message("Recaptcha solucionado!",'\033[92m')
                                return False
                            else:
                                raise Exception(error)
                    else:
                        print_log(" - Procurando frame na página!")
                print_log(" - Recaptcha não foi encontrado nesta página!")
                return False
    except Exception as error:
        print_error("Recaptcha retornou um erro!",'\033[31m',error)
    finally:
        delete_audio(AUDIO_PATH)
        return page


# Find the google frame and click on the checkbox
async def recaptcha_click(page):
    await page.wait_for_load_state()
    frames = page.frames
    for frame in frames:
        if await frame.is_visible(".recaptcha-checkbox-border"):
            print_log(" - Recaptcha checkbox encontrado!")
            await frame.click(".recaptcha-checkbox-border", delay=500)
            return frames
        else:
            print_log(" - Procurando Recaptcha checkbox...")
    print_log(" - Recaptcha checkbox não foi encontrado...")
    return frames
async def check_green_mark(frames):
    for frame in frames:
        await frame.wait_for_load_state() 
        if frame.url.find('api2/anchor') != -1:
            await frame.wait_for_timeout(500)    
            if await frame.is_visible(".recaptcha-checkbox-checked"):
                return True
        else:
            print_log(" - Verificando se checkbox já foi solucionado ...")    
    print_log(" - Recaptcha checkbox não foi solucionado!")
    return False

# If ReCaptcha asks to solve an image quiz, the audio button gonna be clicked
async def recaptcha_audio_button(frame):
    try:               
        await frame.wait_for_selector("#recaptcha-audio-button",timeout=4000)        
        print_log(" - Botão de audio encontrado!")
        await frame.click("#recaptcha-audio-button",timeout=4000)
    except Exception as error:
        print_error("Botão de audio não encontrado!",'\033[31m',error)

count = 0  
timeout = 500 
async def challenge_solver(frame):
    global count, timeout
    try:           
        print_log(" - Frame de audio encontrado!")
        # Note: Find a better selector to wait for    
        href = await frame.get_attribute(".rc-audiochallenge-tdownload-link", "href",timeout=4000)
        print_log(" - Audio link encontrado!")
        # Download the audio from a request 
        audio_file = requests.get(href) 
        await frame.wait_for_timeout(timeout)           
        with open('audio.mp3', 'wb') as f:
            f.write(audio_file.content) 
        print_log(" - Audio baixado!") 
        print_log(" - Resolvendo desafio de audio...")
        text = string_parser(audio_recognize())
        await frame.wait_for_timeout(timeout)
        if text == "":
            print_log(" - Texto vazio, tentando novamente!")
            await frame.click("#recaptcha-reload-button",timeout=4000)
            await challenge_solver(frame)
        print_log(" - Texto reconhecido: " + text)
        print_log(" - Digitando texto e verificando!")
        await frame.fill("#audio-response", text, timeout=4000)  
        await frame.click('#recaptcha-verify-button',delay=500)
        print_log(" - Aguardando verificação...")
        await frame.wait_for_timeout(timeout)
        if await frame.is_visible(".rc-audiochallenge-error-message"):
            print_log(" - Recaptcha solicitando multiplas soluções de áudio!")
            count +=1
            if count >= 5:
                print_log(" - Recaptcha está demorando muito, tentando novamente!")
                timeout = 800
            print_log(" - Recarregando desafio de audio...")
            await frame.wait_for_timeout(timeout)
            await frame.click("#recaptcha-reload-button")
            await challenge_solver(frame)  
    except Exception as error:
        raise Exception(error)

def audio_recognize():
    
    # reading audio
    audio = read_audio(AUDIO_PATH)
    
    # defining headers for HTTP request
    headers = {'authorization': 'Bearer ' + WIT_ACCESS_TOKEN,
               'Content-Type': 'audio/mpeg3'}

    # making an HTTP post request
    resp = requests.post(API_ENDPOINT, headers = headers,
                         data = audio)
    
    # return the text
    return resp.text

def read_audio(AUDIO_FILENAME):
    with open(AUDIO_FILENAME, 'rb') as f:
        audio = f.read()
    return audio

def string_parser(data):
    try:
        final_return = ""
        for str in data.split("\n"):
            # Return a new string without spaces
            str_striped = str.strip()
            #Replace all the double quotes 
            str_replaced = str_striped.replace('"',"")
            if str_replaced.startswith("text"):
                # Remove the text string
                str_final = str_replaced.replace('text: ',"")
                # It's only to remove a single comma :D
                final_return = str_final.replace(',',"")
        return final_return
    except Exception as error:
        print_error("Erro ao parserar string!",'\033[31m',error)

def delete_audio(AUDIO_PATH):
    if os.path.exists(AUDIO_PATH):
      os.remove(AUDIO_PATH)


# Print a message in the console and save it in a log file
def print_message(message,color,character="="):
    message = message.upper() # Convert message to uppercase
    message_length = len(message) # Get the length of the message
    message_center = int((80 - message_length) / 2) # 80 is the screen width 
    # print in bold
    print("\033[1;32m")
    print(color +character * 80, end="\n") # Print the first line
    print(color + character * message_center, end="") # Print the first part of the message
    print(message, end="") # Print the message
    print(character * (80 - message_center - message_length), end="\n") # Print the second part of the message
    print(color +character * 80) # Print the last line
    print("\n")

# Print a error message in the console and save it in a log file
def print_error(message,color, error,character="="):
    # print in bold
    print("\033[1;32m")
    print_message(message,color)
    print(" - DESCRIÇÃO DO ERRO --> ", error)
    print('\033[92m') # Reset terminal color to green

def print_log(message):
    print(message)
    

