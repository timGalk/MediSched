from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def inline_builder(
        text: str | list[str],
        callback_data: str | list[str],
        sizes: int | list[int]=2,
        **kwargs
) -> InlineKeyboardMarkup:
    """The class was created by Tsimur"""
    """
    Builds an InlineKeyboardMarkup object from given text, callback data, and sizes.

    Parameters:
    text: str or list[str]
        The text to display on the inline buttons. Can be a single string or a list of strings.
    callback_data: str or list[str]
        The data to be sent back when the buttons are pressed. Can be a single string or a list of strings.
    sizes: int or list[int], optional
        Specifies the size of rows in the inline keyboard. It can be a single integer or a list of integers indicating the number of buttons per row. Defaults to 2.
    **kwargs: dict
        Additional keyword arguments to pass to the InlineKeyboardBuilder's `as_markup` method.

    Returns:
    InlineKeyboardMarkup
        An InlineKeyboardMarkup object created with the given parameters.
    """
    builder = InlineKeyboardBuilder()
    if isinstance(text, str):
        text = [text]
    if isinstance(callback_data, str):
        callback_data = [callback_data]
    if isinstance(sizes, int):
        sizes = [sizes]

    [
        builder.button(text=txt, callback_data=cb)
        for txt, cb in zip(text, callback_data)
    ]

    builder.adjust(*sizes)
    return builder.as_markup(**kwargs)