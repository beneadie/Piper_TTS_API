import subprocess
import os
from random import randint
import soundfile as sf
import numpy as np
import asyncio

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize


""""
Max lenght a command line can be is 8191 characters. text hence must be broken up or multiprocessed
"""

voices_dict = {
     "irishGirl": ["\en_GB-jenny_dioco-medium.onnx", "\en_en_GB_jenny_dioco_medium_en_GB-jenny_dioco-medium.onnx.json", ""],
     "usaGirl" : ["\en_US-hfc_female-medium.onnx", "\en_en_US_hfc_female_medium_en_US-hfc_female-medium.onnx.json", ""],
     "usaBoy" : ["\en_US-hfc_male-medium.onnx", "\en_en_US_hfc_male_medium_en_US-hfc_male-medium.onnx.json", ""],
     "scotGirl" : ["\en_GB-alba-medium.onnx", "\en_en_GB_alba_medium_en_GB-alba-medium.onnx.json", ""],
     #"englishNorthBoy" : ["\en_GB-northern_english_male-medium.onnx", "\en_en_GB_northern_english_male_medium_en_GB-northern_english_male-medium.onnx.json", ""],
     #"usaJoe" : ["\en_US-joe-medium.onnx", "\en_en_US_joe_medium_en_US-joe-medium.onnx.json", ""],
     #"usaAmy" : ["\en_US-amy-medium.onnx", "\en_en_US_amy_medium_en_US-amy-medium.onnx.json"],
     "usaShelly" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 652"],
     "usaStan" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 291"],
     "usaEric" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 730"],
     "usaLeopold" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 386"],
     "usaKyle" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 478"],
     "usaMel" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 495"],
     "usaSophie" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 349"],
     "usaAnne" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 64"],
     "usaHeidi" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 1"],
     "usaLeopold" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 7"],
     "usaRyan" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 134"],
     "usaKenny" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 49"],
     "usaScott" : ["/en_US-libritts_r-medium.onnx", "/en_en_US_libritts_r_medium_en_US-libritts_r-medium.onnx.json", " --speaker 898"]
}
title_abbreviation_dict = {
    "U.S": "United States ",
    "US": "United States ",
    "bioinformatics": "bio informatics",
    "Bioinformatics": "Bio informatics",
    " Dr.": " Doctor",
    " Mr.": " Mister",
    " Mrs.": " Missus",
    " Ms.": " Miss",
    " Prof.": " Professor",
    " Rev.": " Reverend",
    " Fr.": " Father",
    #"Sr.": "Sister",
    "Br.": "Brother",
    "Capt.": "Captain",
    "Cmdr.": "Commander",
    "Col.": "Colonel",
    "Gen.": "General",
    "Adm.": "Admiral",
    "Lt.": "Lieutenant",
    #"Ltd.": "Limited",
    "Ltd": "Limited",
    "Maj.": "Major",
    "Sgt.": " Sergeant",
    "Cpl.": " Corporal",
    "Pvt.": " Private",
    "Gov.": " Governor",
    "Airbnbs": "Air B N B's", #sounds better
    "Airbnb's": "Air B N B's",
    "Airbnb": "Air B N B",
    "airbnb": "Air B N B",
    "AirBnb": "Air B N B",
    "AirBnB": "Air B N B",
    "YC": "Y C",
    "YC's": "Y C's",
    "yc": "Y C",
    "Yc": "Y C",
    "AIs": "A I's",
    "AI's": "A I's",
    "AI" : " A I",
    "AI." : "A I.",

    #"Rep.": "Representative",
    #"Sen.": "Senator",
    "Sec.": "Secretary",
    "Treas.": "Treasurer",
    #"VP": "Vice President",
    #"Pres.": "President",
    "Amb.": "Ambassador",
    "Atty.": "Attorney",
    "Ave" : "Avenue",
    "Ave." : " Avenue.",
    "AI, " : " A I, ",
    "VRAM. " : "V RAM.",
    "GPT" : " G P T ",
    "GPT." : " G P T.",
    "gpt" : "g p t",
    "gpt," : "g p t,",
    "gpt." : "g p t.",
    "GPT?" : "g p t?",
    "GPT?" : "G P T?",
    "gpt?" : "g p t?",
    "psychology?" : "sigh chology",
    "psycho" : "sigh koe",
    "psychological" : "sigh chological",
    "psychiatric" : "sigh chiatric",
    "psyche" : "sigh key",
    "psychoanalyst" : "sigh choanalyst",
    "psychoanalysis" : "sigh choanalysis",

}

letter_dict_abbrev = {
    'A. ': ' A, ', 'B. ': ' B, ', 'C. ': ' C, ', 'D. ': ' D, ', 'E. ': ' E, ', 'F. ': ' F, ', 'G.': ' G, ', 'H. ': ' H, ', 'I. ': ' I, ', 'J. ': ' J, ',
    'K.': ' K, ', ' L. ': ' L, ', 'M. ': ' M, ', 'N. ': ' N, ', 'O. ': ' O, ', 'P. ': ' P, ', 'Q.': ' Q, ', 'R. ': ' R, ', 'S. ': ' S, ', 'T. ': ' T, ',
    'U.': ' U, ', ' V. ': ' V, ', 'W. ': ' W, ', 'X. ': ' X, ', 'Y. ': ' Y, ', 'Z. ': ' Z, '#,
    #' b. ': ' b ', ' c.': ' c ', ' d. ': ' d ', ' e. ': ' e ', ' f. ': ' f ', ' g. ': ' g ', ' h. ': ' h ', ' i. ': ' i ', ' j. ': ' j ',
    #' k.': ' k ', ' l. ': ' l ', ' m.': ' m ', ' n. ': ' n ', ' o. ': ' o ', ' p. ': ' p ', ' q. ': ' q ', ' r. ': ' r ', ' s. ': ' s ', ' t. ': ' t ',
    #' u.': ' u ', ' v. ': ' v ', ' w.': ' w ', ' x. ': ' x ', ' y. ': ' y ', ' z. ': ' z '
}

def check_next_word_name(text, position):
    """idea to make a way of checking if the next word is a name so that you
      can decide what to do with prefixes"""
    pass

def convert_abbreviations(text, letter_dict_abbrev=letter_dict_abbrev, title_abbreviation_dict=title_abbreviation_dict):
    for key, value in title_abbreviation_dict.items():
        text = text.replace(key, value)
    for key, value in letter_dict_abbrev.items():
        text = text.replace(key, value)
    return text

def replace_newlines_with_spaces(text):
    #text = text.replace("\n", "")
    text = text.replace("*", " ")
    text = text.replace(";", "., ")
    text = text.replace(":", "., ")
    text = text.replace("(", ",(")
    text = text.replace(")", "),")
    # not sure if this one is right choice
    text = text.replace("-", " ")

    return text


def run_piper(input_text, model_path, config_path, speaker, output_file):
    # Replace newline characters with spaces
    input_text = input_text.replace("\n", " ")

    # Construct the command
    command = f'echo "{input_text}" | .\piper\piper.exe -m .\piper\models"{model_path}" -c .\piper\models\"{config_path}" -f .\outputs"{output_file}" --cuda{speaker}'

    # Execute the command
    subprocess.run(command, shell=True)

def checkIfNoFolder(folder):
    if os.path.exists(f"./outputs/{folder}") and os.path.isdir(f"./outputs/{folder}"):
        return True
    else:
        try:
            os.makedirs(f"./outputs/{folder}")
            return True
        except OSError as e:
            return False

def delete_files(file_names):
    for file_name in file_names:
        try:
            os.remove(file_name)
        except OSError as e:
            print(f"Error deleting file '{file_name}': {e}")

def wavjoin(wav_files, userid, filename):
    audio_data = []
    # Iterate over each WAV file
    for file in wav_files:
        # Read the WAV file
        data, samplerate = sf.read(file)
        # Append the audio data to the list
        audio_data.append(data)
    # Concatenate the audio data
    combined_audio = np.concatenate(audio_data)
    # Write the combined audio data to a new WAV file
    sf.write(f'./outputs/{userid}/{filename}.wav', combined_audio, samplerate)

def callLongTextPiper(text, model_name="scotGirl", userid="public", identifier=randint(0,9999999)):
    if type(identifier) != int:
        identifier += str(randint(0,99999))
        text = ".. " + text
        print("made it to callLongTextPiper")
        sentences = sent_tokenize(text)
        #sentences = ["I like cock.", "I like boobs.", "I like boobs.", "I like boobs."]
        #print("made it past sent_tokenize")

        divides = (len(text) // 3500) + 1
        # if doesn't divide equally it needs to be assigned
        remains = len(sentences) % divides
        block_size = len(sentences) // divides
        prev_index = 0
        curr_index = block_size
        text_arr = []

        # Calculate the base value for each number
        base_value = remains // divides
        # Calculate the remainder
        remainder = remains % divides
        # Initialize the result array
        arr_remain = [base_value] * divides
        # Distribute the remainder evenly
        for i in range(remainder):
            arr_remain[i] += 1
        count = 0
        while curr_index <= len(sentences):

            curr_index += arr_remain[count]
            block = sentences[prev_index:curr_index]
            joined_text = '. '.join(block)
            text_arr.append(joined_text)
            prev_index = curr_index
            curr_index += block_size
            count+=1
        #identifier = randint(0,9999999)
        count = 1
        file_names = []
        print("made it to call_piper_gaps_and_pause")
        for textblock in text_arr:
            piper_arr = call_piper_gaps_and_pause(textblock, model_name, userid, f"temp{count}_${identifier}")
            path_to_file = piper_arr[0]
            #name = piper_arr[1]
            file_names.append(path_to_file)
            count+=1
        #print(file_names)
        #join the wav files
        wavjoin(file_names, userid, f"{identifier}_{model_name}")
        delete_files(file_names)
        return [f"./outputs/{userid}/{identifier}_{model_name}.wav", f"{identifier}_{model_name}"]

        return "you failed at sentence_tokenize"



def call_piper(input_text=".Error.No text submitted.", model_name="scotGirl", userid="public", identifier=randint(0,9999999)):
    if checkIfNoFolder(f"{userid}") == False:
        return "unable to create folder"
    if type(identifier) != int:
        identifier += str(randint(0,99999))
    input_text = ".. " + input_text
    cleaned_text = replace_newlines_with_spaces(input_text)
    cleaned_text = convert_abbreviations(cleaned_text)

    if model_name in voices_dict:
        model_path = voices_dict[model_name][0]
        config_path = voices_dict[model_name][1]
        speaker = voices_dict[model_name][2]
        name = f"{identifier}_{model_name}"
        output_file = f"/{userid}/{name}.wav"
    else:
        model_path = voices_dict["scotGirl"][0]
        config_path = voices_dict["scotGirl"][1]
        speaker = voices_dict["scotGirl"][2]
        name = f"{identifier}_scotGirl"
        output_file = f"/{userid}/{name}.wav"
    run_piper(cleaned_text, model_path, config_path, speaker, output_file)
    return [f"./outputs{output_file}", name]

def call_piper_gaps_and_pause(text, model_name="scotGirl", userid="public", identifier=randint(0,9999999)):
    array_of_paragraphs = text.split('\n')
    # creating array that also has space file for each new line
    file_names = []
    deletion_list = []
    count = 1
    for textblock in array_of_paragraphs:
        piper_arr = call_piper(textblock, model_name, userid, f"temp{count}_${identifier}")
        path_to_file = piper_arr[0]
        #name = piper_arr[1]
        deletion_list.append(path_to_file)
        file_names.append(path_to_file)
        file_names.append("./outputs/silent.wav")
        count+=1
    wavjoin(file_names, userid, f"{identifier}_{model_name}")
    delete_files(deletion_list)
    return [f"./outputs/{userid}/{identifier}_{model_name}.wav", f"{identifier}_{model_name}"]






def delete_file(file_path):
    os.remove(file_path)

# Asynchronous wrappers for the synchronous functions
async def call_piper_async(input_text, model_name, userid, name_file):
    return await asyncio.to_thread(call_piper, input_text, model_name, userid, name_file)

async def callLongTextPiper_async(input_text, model_name, userid, name_file):
    return await asyncio.to_thread(callLongTextPiper, input_text, model_name, userid, name_file)


def get_voices():
    keysList = list(voices_dict.keys())
    return keysList
