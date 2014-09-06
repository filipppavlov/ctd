import re
import config

_EQUIVALENCE_RE = re.compile(re.escape(config.VARIABLE_DELIMS[0]) + '([^' + re.escape(config.WORD_SEPARATOR) +
                             re.escape(config.VARIABLE_DELIMS[1]) + ']*)' + re.escape(config.VARIABLE_DELIMS[1]))


def validate_path(path):
    if path == '':
        raise ValueError('path is empty')
    for each in split(path):
        if each == '':
            raise ValueError('path component is empty')


def get_equivalence_class_name(path):
    validate_path(path)
    return _EQUIVALENCE_RE.sub(config.CLASS_WILDCARD, path)


def split(path):
    return path.split(config.WORD_SEPARATOR)


def join(*args):
    path = ''
    for each in args:
        if path == '':
            path = each
        else:
            path += config.WORD_SEPARATOR + each
    return path


def encode_special_symbols(string, encoded_class_wildcard, encoded_word_separator, encoded_variable_delims):
    repl = encoded_variable_delims[0] + r'\1' + encoded_variable_delims[1]
    string = _EQUIVALENCE_RE.sub(repl, string)
    string = string.replace(config.CLASS_WILDCARD, encoded_class_wildcard)
    return string.replace(config.WORD_SEPARATOR, encoded_word_separator)


def decode_special_symbols(string, encoded_class_wildcard, encoded_word_separator, encoded_variable_delims):
    pattern = re.compile(re.escape(encoded_variable_delims[0]) + '([^' + re.escape(encoded_word_separator) +
                             re.escape(encoded_variable_delims[1]) + ']*)' + re.escape(encoded_variable_delims[1]))
    repl = config.VARIABLE_DELIMS[0] + r'\1' + config.VARIABLE_DELIMS[1]
    string = re.sub(pattern, repl, string)
    string = string.replace(encoded_class_wildcard, config.CLASS_WILDCARD)
    return string.replace(encoded_word_separator, config.WORD_SEPARATOR)