# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import sys, os, vk_api, datetime

UserId = ""
vk_session = vk_api

#authantication
print("Введите токен: ")
token = input()
try:
    vk_session = vk_api.VkApi(token=token)
except Exception as e:
    print(e)
else:
    print('Успешный вход!')
def saveData(tag, data, fid=""):
    global UserId
    LogFile = open(str(UserId) + "_" + tag + fid +".txt", 'w', encoding="utf-8")
    LogFile.write(data)

def normalizeSex(sex):
    if sex == 2:
        return "Мужской"
    elif sex == 1:
        return "Женский"
    else:
        return "none"

def normalizeCP(CP):
    if str(CP) == "False":
        return "нет"
    else:
        return "да"

def normalizeStatus(status):
    if status == 1:
        return "прочитано"
    else:
        return "не прочитано"

def normalizeLocation(location):
    if location != None:
        return dict(location).get("title")
    else:
        return "не выбрано"

def getProfileData():
    print("Сбор данных профиля...")
    global UserId
    ProfileData = vk_session.method('users.get', {
                                        'fields': "first_name, last_name, is_closed, photo_200_orig, sex, bdate, city, country, status, followers_count, about",
                                        })
    
    UserId = str(ProfileData[0].get("id"))
    print("User id: " + UserId)
    ResData = "ID пользователя: " + str(UserId) + "\nИмя: " + ProfileData[0].get("first_name") + "\nФамилия: " + ProfileData[0].get("last_name")  + "\nПол: " + normalizeSex(ProfileData[0].get("sex")) + "\nО себе: " + ProfileData[0].get("about")+ "\nЗакртытая страница: " + normalizeCP(ProfileData[0].get("is_closed")) + "\nФото: " + ProfileData[0].get("photo_200_orig") + "\nДень рождения: " + ProfileData[0].get("bdate") + "\nСтрана: " + str(ProfileData[0].get("country").get("title")) + "\nГород: " + str(ProfileData[0].get("city").get("title")) + "\nПодписчиков: " + str(ProfileData[0].get("followers_count"))
    saveData("Profile", ResData)
    print("Успешно")
    
def getDialogs():
    print("Сбор диалогов...")
    Dialogs = vk_session.method('messages.getDialogs', {
                                        'count': 200
                                        })
    ResData = "Количество диалогов: " + str(Dialogs.get("count"))
    for item in Dialogs.get("items"):
        ResData += "\n\nДиалог с пользователем: " + "https://vk.com/id" + str(item.get("message").get("user_id")) + "\nДата последнего сообщения: " + str(datetime.datetime.fromtimestamp(item.get("message").get("date"))) + "\nСтатус: " + normalizeStatus(item.get("message").get("read_state")) + "\nПоследнее сообщение: " + item.get("message").get("body")
    saveData("Messages", ResData)
    print("Успешно")

def getFriends():
    print("Сбор данных о друзьях...")
    Friends = vk_session.method('friends.get', {
                                        'order': "hints",
                                        'count': 5000,
                                        'fields':"sex, city, country, last_seen"
                                        })
    ResData = "Количество друзей: " + str(Friends.get("count"))
    for item in Friends.get("items"):
        ResData += "\n\nПользователь: " + item.get("first_name") + " " +  item.get("last_name") + " " +"https://vk.com/id" + str(item.get("id")) + "\nПол: " + normalizeSex(item.get("sex")) + "\nСтрана: " + normalizeLocation(item.get("country")) + "\nГород: " + normalizeLocation(item.get("city"))
    saveData("Friends", ResData)
    print("Успешно")

#ForDialogs

def getUzverName(uzver_id):
    global UserId
    ProfileData = vk_session.method('users.get', {
                                        'user_ids': uzver_id,
                                        'fields': "first_name, last_name, id"
                                        })
    if uzver_id == None:
        UserId = str(ProfileData[0].get("id"))
    return ProfileData[0].get("first_name") + " " + ProfileData[0].get("last_name")

def getAttachments(attachments):
    if list(attachments) != []:
        ResData = "\nВложения: "
        for item in attachments:
            if item.get("type") == 'photo':
                ResData += "\n\tФото: " + item.get("photo").get("sizes")[len(item.get("photo").get("sizes"))-1].get("url")
            if item.get("type") == 'video':
                ResData += "\n\tВидео: " + "https://vk.com/video" + str(item.get("video").get("owner_id")) + "_" + str(item.get("video").get("id"))
        return ResData

def getDialog(user_id):
    print("Сбор сообщений...")
    myName = getUzverName(None)
    friendName = getUzverName(user_id)
    Dialog = vk_session.method('messages.getHistory', {
                                        'count': 200,
                                        'user_id': user_id,
                                        'extended': 1
                                        })
    def getName(uid):
        if uid == user_id:
            return friendName
        else:
            return myName
    ResData = "Количество сообзений: " + str(Dialog.get("count"))
    for item in Dialog.get("items"):
        ResData += "\n\nСообщение от : " + getName(item.get("from_id")) +" " + str(datetime.datetime.fromtimestamp(item.get("date"))) + "\nТекст: " + item.get("text") + str(getAttachments(item.get("attachments")))
    saveData("Dialog", ResData, " " + friendName)
    print("Успешно")


print("Выберите действие:\n1. Собрать информацию о профиле\n2. Получить диалог с пользователем по его id")
do = int(input())
if do == 1:
    getProfileData()
    getDialogs()
    getFriends()
elif do == 2:
    print("Введите id нужного пользователя: ")
    uzver_id = int(input())
    if uzver_id != None:
        getDialog(uzver_id)
    else:
        print("Неверный id!")
else:
    print("Неверное значение!")
