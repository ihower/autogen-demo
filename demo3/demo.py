import autogen

import requests
import json
from pydub import AudioSegment
from pydub.playback import play
import os

openai_api_key = "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"
def speak(message, voice="echo"):
    text = message["content"]

    file_name = f"{text[:30].replace(' ', '_')}.mp3"

    if not os.path.isfile(file_name):
        # voice 有 alloy, echo, fable, onyx, nova, and shimmer
        if message["name"] == 'Audience':
            voice = "nova"
        elif message["name"] == 'Niceguy':
            voice = "echo"
        elif message["name"] == 'Badguy':
            voice = "fable"

        payload = { "model": "tts-1", "input": text, "voice": voice, "speed": 1.1 }
        headers = { "Authorization": f'Bearer {openai_api_key}', "Content-Type": "application/json" }
        response = requests.post('https://api.openai.com/v1/audio/speech', headers = headers, data = json.dumps(payload) )

        with open(file_name, 'wb') as audio_file:
            audio_file.write(response.content)

    audio = AudioSegment.from_file(file_name, format="mp3")
    play(audio)

llm_config1 = {
#  "cache_seed": 100,  # change the cache_seed for different trials
 "temperature": 0.4,
 "config_list": autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview"] # ["gpt-3.5-turbo-1106"]
    },
 ),
 "timeout": 120,
}

llm_config2 = {
 "temperature": 0.4,
 "config_list": autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview"]
    },
 ),
 "timeout": 120,
}

user_proxy = autogen.UserProxyAgent(
   name="Audience",
   code_execution_config=False,
   human_input_mode="ALWAYS"
)

joker1 = autogen.AssistantAgent(
    name="Niceguy",
    llm_config=llm_config1,
    system_message='''你是一位漫才表演者，擔任較滑稽的角色負責裝傻。以下是你和另一位漫才搭擋進行對話，你的任務是進行鋪陳。
你只扮演你自己講幾句話，不要扮演搭擋。一次講一個簡短段子就好，100字以內，不要急著下台感謝聽眾。
    ''',
    code_execution_config=False
)

joker2 = autogen.AssistantAgent(
    name="Badguy",
    llm_config=llm_config2,
    system_message="""你是一位漫才表演者，擔任較嚴肅的角色負責吐槽。以下是你和另一位漫才搭擋進行對話，你的任務是針對對方說的話，進行搞笑吐槽，請簡短有梗。
你只扮演你自己講幾句話，不要扮演搭擋。
""",
    code_execution_config=False
)

groupchat = autogen.GroupChat(agents=[user_proxy, joker1, joker2], messages=[], max_round=50, speaker_selection_method="round_robin")
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config2)

def print_messages(recipient, messages, sender, config):
    if "callback" in config and  config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])
    # print(f"Messages sent to: {recipient.name} | num messages: {len(messages)} | {messages[-1]}")
    speak(messages[-1])
    return False, None

user_proxy.register_reply(
 [autogen.Agent, None],
 reply_func=print_messages,
 config={"callback": None},
)

joker1.register_reply(
 [autogen.Agent, None],
 reply_func=print_messages,
 config={"callback": None},
)

joker2.register_reply(
 [autogen.Agent, None],
 reply_func=print_messages,
 config={"callback": None},
)


user_proxy.initiate_chat(
    manager,
    message="""
請開始一段主題是「2023 忘年會」的脫口秀表演
""",
)


