

def get_members(channel):
    members = []
    for owners in channel['owners']:
        members.append(owners['username'])
    for admins in channel['admins']:
        if admins['username'] not in members:
            members.append(admins['username'])
    for writers in channel['writers']:
        if writers['username'] not in members:
            members.append(writers['username'])
    for readers in channel['readers']:
        if readers['username'] not in members:
            members.append(readers['username'])
    return members


def get_user(channel):
    members = []
    for owners in channel['owners']:
        members.append(owners['username'])
    for admins in channel['admins']:
        if admins['username'] not in members:
            members.append(admins['username'])
    for writers in channel['writers']:
        if writers['username'] not in members:
            members.append(writers['username'])
    for readers in channel['readers']:
        if readers['username'] not in members:
            members.append(readers['username'])
    return members
