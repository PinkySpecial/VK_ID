import requests
import networkx as nx
import plotly.graph_objects as go
import time
import collections

# Ваш access token для VK API
access_token = 'Ваш токен'

# ID пользователя, чьих друзей Вы хотите получить
user_id = '224364474'

# Функция для получения списка друзей пользователя
def get_friends(user_id):
    api_url = f'https://api.vk.com/method/friends.get?user_id={user_id}&count=1000&access_token={access_token}&v=5.131'
    response = requests.get(api_url)
    friends_data = response.json()
    if 'error' in friends_data:
        print(f"Ошибка: {friends_data['error']['error_msg']}")
        return []
    else:
        return friends_data['response']['items']

# Функция для получения информации о друзьях
def get_friends_info(user_ids):
    api_url = f'https://api.vk.com/method/users.get?user_ids={",".join(map(str, user_ids))}&access_token={access_token}&v=5.131'
    response = requests.get(api_url)
    friends_info_data = response.json()
    if 'error' in friends_info_data:
        print(f"Ошибка: {friends_info_data['error']['error_msg']}")
        return []
    else:
        return friends_info_data['response']


# Функция для получения друзей друзей
def get_friends_of_friends(user_ids):
    i=0
    friends_of_friends = []
    for user_id in user_ids:
        i=i+1
        friends = get_friends(user_id)
        friends_of_friends.extend(friends)
        time.sleep(0.5)
    return friends_of_friends


# Получение списка друзей пользователя
user_friends = get_friends(user_id)

# Получение информации о друзьях
user_friends_info = get_friends_info(user_friends)

# Получение друзей друзей
user_friends_of_friends = get_friends_of_friends(user_friends)

# Создание графа
G = nx.Graph()

# Добавление вершины для пользователя
G.add_node(user_id)

# Добавление вершин для друзей
G.add_nodes_from(user_friends)

# Добавление вершин для друзей друзей
G.add_nodes_from(user_friends_of_friends)

# Добавление ребер между пользователем и его друзьями
for friend in user_friends:
    G.add_edge(user_id, friend)

# Добавление ребер между друзьями и их друзьями
for friend in user_friends:
    friends_of_friend = get_friends(friend)
    G.add_edges_from([(friend, fof) for fof in friends_of_friend])
    time.sleep(0.5)

# Расчет позиций вершин в круговом расположении
pos = nx.spring_layout(G)

# Создание графика Plotly
fig = go.Figure()

# Добавление ребер в график
for edge in G.edges:
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines'))

# Добавление вершин в график
for node in G.nodes:
    x, y = pos[node]
    fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(size=10), text=node, name=node))

# Добавление информации о количестве связей
for node in G.nodes:
    x, y = pos[node]
    friends_count = len(list(G.neighbors(node)))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(size=10), text=f"{node}\nКоличество связей: {friends_count}", name=node))

# Установка расположения и заголовка
fig.update_layout(title='Граф друзей и их друзей')

fig.show()