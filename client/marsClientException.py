class MarsClientException(Exception):
    '''
    We want a method unique to our client to throw known possible
    issues that could occur, hense a little inheritance
    '''
    pass
