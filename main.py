import streamlit as st

from api import get_characterglm_response
from logger import LOG

button_labels = {
    "start_chat": "开始对话",
    # "auto_generate_character": "生成人设",
    # "clear_meta": "清空人设",
    "clear_history": "清空对话历史"
}


def init_session():
    st.session_state["role1_history"] = []
    st.session_state["role2_history"] = []


# 4个输入框，设置meta的4个字段, 角色1和角色2
meta_labels = {
    "role1_name": "角色1名字",
    "role2_name": "角色2名字",
    "role1_info": "角色1人设",
    "role2_info": "角色2人设"
}


def reset():
    LOG.info(st.session_state)
    st.session_state["meta"] = {
        "role1_name": "角色1",
        "role2_name": "角色2",
        "role1_info": "身高185cm，体重75kg，发型整洁短发，现代精英男，英俊潇洒，腰缠万贯，忠贞不渝",
        "role2_info": "身高165cm，体重55kg，长发飘飘，可爱励志女，志向高远，勇敢追梦，终成人生赢家"
    }


# 初始化
if "role1_history" not in st.session_state:
    st.session_state["role1_history"] = []
if "role2_history" not in st.session_state:
    st.session_state["role2_history"] = []
if "meta" not in st.session_state:
    reset()


# st.session_state["meta"] = {
#     "role1_name": "",
#     "role2_name": "",
#     "role1_info": "",
#     "role2_info": ""
# }


def verify_meta() -> bool:
    LOG.info(f'session_state.meta: {st.session_state["meta"]}')
    # 检查`角色名`和`角色人设`是否空，若为空，则弹出提醒
    if st.session_state["meta"]["role1_name"] == "" \
            or st.session_state["meta"]["role1_info"] == "" \
            or st.session_state["meta"]["role2_name"] == "" \
            or st.session_state["meta"]["role2_info"] == "":
        st.error("角色名和角色人设不能为空")
        return False
    else:
        return True


# 2x2 layout
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(label=meta_labels["role1_name"], key="role1_name", value="角色1",
                      on_change=lambda: st.session_state["meta"].update(role1_name=st.session_state["role1_name"]),
                      help="角色1的名字，不可以为空")
        st.text_area(label=meta_labels["role1_info"], key="role1_info",
                     value=st.session_state["meta"]["role1_info"],
                     on_change=lambda: st.session_state["meta"].update(role1_info=st.session_state["role1_info"]),
                     help="角色1的详细人设信息，不可以为空")

    with col2:
        st.text_input(label=meta_labels["role2_name"], value="角色2", key="role2_name",
                      on_change=lambda: st.session_state["meta"].update(role2_name=st.session_state["role2_name"]),
                      help="角色2的名字")
        st.text_area(label=meta_labels["role2_info"],
                     value=st.session_state["meta"]["role2_info"],
                     key="role2_info",
                     on_change=lambda: st.session_state["meta"].update(role2_info=st.session_state["role2_info"]),
                     help="角色2的详细人设信息，可以为空")


def show_role1_say(say):
    with st.chat_message(name="user", avatar="user"):
        st.markdown(say)


def show_role2_say(say):
    with st.chat_message(name="assistant", avatar="assistant"):
        st.markdown(say)


def start_chat():
    # role1作为用户
    role1_character_meta = {
        "user_info": st.session_state["meta"]["role1_info"],
        "bot_info": st.session_state["meta"]["role2_info"],
        "user_name": st.session_state["meta"]["role1_name"],
        "bot_name": st.session_state["meta"]["role2_name"],
    }
    # role2 作为用户
    role2_character_meta = {
        "user_info": st.session_state["meta"]["role2_info"],
        "bot_info": st.session_state["meta"]["role1_info"],
        "user_name": st.session_state["meta"]["role2_name"],
        "bot_name": st.session_state["meta"]["role1_name"],
    }
    messages = [
        {"role": "assistant",
         "content": "你是一个懂得日常聊天机器人，基于我给的两个人设的信息，以角色1的身份，随机给出一个和角色2日常在日常工作中开始聊天的话，回答里不要包含角色名"},
        {"role": "user",
         "content": f'人设一: {st.session_state["meta"]["role1_info"]}, 人设二：{st.session_state["meta"]["role2_info"]}'}
    ]
    LOG.info(f'start message: {messages}')
    role1_say = ""
    role2_say = ""
    st.session_state["role2_history"] += [{"role": "user",
                                           "content": f'这是你的人设信息，后面的回答请基于这个人设信息: {role2_character_meta["bot_info"]}'}]
    st.session_state["role1_history"] += [{"role": "user",
                                           "content": f'这是你的人设信息，后面的回答请基于这个人设信息: {role1_character_meta["bot_info"]}'}]

    chat_history = []
    # 给角色1生成一个开场白
    for chunk in get_characterglm_response(messages, role1_character_meta):
        role1_say = chunk
    LOG.info(f'{st.session_state["meta"]["role1_name"]}开场白: {role1_say}')
    show_role1_say(role1_say)
    chat_history.append(f'{st.session_state["meta"]["role1_name"]}: {role1_say}')
    st.session_state["role1_history"] += [{"role": "user", "content": role1_say}]
    st.session_state["role2_history"] += [{"role": "assistant", "content": role1_say}]
    LOG.info(f'role1_history: {st.session_state["role1_history"]}')
    LOG.info(f'role2_history: {st.session_state["role2_history"]}')

    # 把角色2作为角色1的bot人设，让角色1用上面的开场白先发起一个问题
    for chunk in get_characterglm_response(st.session_state["role1_history"], role1_character_meta):
        # 回答作为角色2的机器回答
        role2_say = chunk
    show_role2_say(role2_say)
    chat_history.append(f'{st.session_state["meta"]["role2_name"]}: {role2_say}')
    LOG.info(f'{st.session_state["meta"]["role2_name"]}: {role2_say}')
    st.session_state["role1_history"] += [{"role": "assistant", "content": role2_say}]
    st.session_state["role2_history"] += [{"role": "user", "content": role2_say}]
    #
    for chunk in get_characterglm_response(st.session_state["role2_history"], role2_character_meta):
        # 回答作为角色1的机器回答
        role1_say = chunk
    LOG.info(f'{st.session_state["meta"]["role1_name"]}: {role1_say}')
    show_role1_say(role1_say)
    chat_history.append(f'{st.session_state["meta"]["role1_name"]}: {role1_say}')
    st.session_state["role2_history"] += [{"role": "assistant", "content": role1_say}]
    st.session_state["role1_history"] += [{"role": "user", "content": role1_say}]

    for i in range(5):
        # 把角色2作为角色1的bot人设，让角色1用上面的开场白先发起一个问题
        for chunk in get_characterglm_response(st.session_state["role1_history"], role1_character_meta):
            # 回答作为角色2的机器回答
            role2_say = chunk
        LOG.info(f'{st.session_state["meta"]["role2_name"]}: {role2_say}')
        show_role2_say(role2_say)
        chat_history.append(f'{st.session_state["meta"]["role2_name"]}: {role2_say}')
        st.session_state["role1_history"] += [{"role": "assistant", "content": role2_say}]
        st.session_state["role2_history"] += [{"role": "user", "content": role2_say}]
        #
        for chunk in get_characterglm_response(st.session_state["role2_history"], role2_character_meta):
            # 回答作为角色1的机器回答
            role1_say = chunk
        LOG.info(f'{st.session_state["meta"]["role1_name"]}: {role1_say}')
        show_role1_say(role1_say)
        chat_history.append(f'{st.session_state["meta"]["role1_name"]}: {role1_say}')
        st.session_state["role2_history"] += [{"role": "assistant", "content": role1_say}]
        st.session_state["role1_history"] += [{"role": "user", "content": role1_say}]

    LOG.info(f'role1_history: {st.session_state["role1_history"]}')
    LOG.info(f'role2_history: {st.session_state["role2_history"]}')

    with open('chat.txt', 'a', encoding='utf-8') as file:
        file.writelines("%s\n" % s for s in chat_history)


# 在同一行排列按钮
with st.container():
    n_button = len(button_labels)
    cols = st.columns(n_button)
    button_key_to_col = dict(zip(button_labels.keys(), cols))

    # with button_key_to_col["clear_meta"]:
    #     clear_meta = st.button(button_labels["clear_meta"], key="clear_meta")
    #     if clear_meta:
    #         reset()
    #         st.rerun()

    with button_key_to_col["clear_history"]:
        clear_history = st.button(button_labels["clear_history"], key="clear_history")
        if clear_history:
            init_session()
            st.rerun()

    with button_key_to_col["start_chat"]:
        sc = st.button(button_labels["start_chat"], key="start_chat")
        if sc:
            if not verify_meta():
                pass
            else:
                start_chat()
