class AgentMemory:
    """
    A class to store a list of message dictionaries.
    Each message is represented as a dictionary with two keys:
      - sender (either 'user' or 'chatbot')
      - content (the message string)
    """

    def __init__(self):
        # Initialize the messages list
        self.messages = []

    def add_message(self, sender: str, content: str) -> None:
        """
        Appends a new message to the messages list.

        :param sender: A string representing who sent the message (user" or "chatbot").
        :param content: The content of the message.
        :return: None
        """
        self.messages.append({
            "sender": sender,
            "content": content
        })

    def get_messages(self) -> list:
        """
        Returns the entire list of messages.

        :return: A list of message dictionaries.
        """
        return self.messages

    def clear_messages(self) -> None:
        """
        Empties the list of messages.

        :return: None
        """
        self.messages.clear()
