#  Chat Server using python socket



- `/join <channel>` should add the client to the given channel.  Clients can only be in one channel at a time, so if the client is already in a channel, this command should remove the client from that channel. When a client is added to a channel, a message should be broadcasted to all existing members of the channel stating that the client has joined.  Similarly, if the client left a channel, a message should be broadcasted stating that the client left.
- `/create <channel>` should create a new channel with the given name, and add the client to the given channel.  As with the `/join` call, the client should be removed from any existing channels.
- `/list` should send a message back to the client with the names of all current channels, separated by newlines.
