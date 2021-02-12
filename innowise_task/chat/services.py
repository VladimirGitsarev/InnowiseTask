
def is_chat_available(profile, chat) -> bool:
    '''Check if user is a participant of current chat'''
    return chat.user1 == profile or chat.user2 == profile