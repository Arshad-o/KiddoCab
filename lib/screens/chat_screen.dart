import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ChatScreen extends StatefulWidget {
  final String otherUserId;
  final String otherUserName;

  const ChatScreen({
    super.key,
    required this.otherUserId,
    required this.otherUserName,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _supabase = Supabase.instance.client;
  final _messageController = TextEditingController();
  
  late final Stream<List<Map<String, dynamic>>> _messagesStream;

  @override
  void initState() {
    super.initState();
    final myId = _supabase.auth.currentUser!.id;
    
    // Listen to messages where we are either the sender or receiver
    // RLS will automatically restrict this to only our messages
    _messagesStream = _supabase
        .from('messages')
        .stream(primaryKey: ['id'])
        .order('created_at', ascending: true);
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;
    
    _messageController.clear();
    
    try {
      await _supabase.from('messages').insert({
        'sender_id': _supabase.auth.currentUser!.id,
        'receiver_id': widget.otherUserId,
        'message': text,
      });
    } catch (e) {
      print('Error sending message: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final myId = _supabase.auth.currentUser?.id;

    return Scaffold(
      appBar: AppBar(
        title: Text('Chat with ${widget.otherUserName}'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: StreamBuilder<List<Map<String, dynamic>>>(
              stream: _messagesStream,
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }

                // Filter messages client-side to only show conversation between these two users
                final messages = snapshot.data!.where((m) => 
                  (m['sender_id'] == myId && m['receiver_id'] == widget.otherUserId) ||
                  (m['sender_id'] == widget.otherUserId && m['receiver_id'] == myId)
                ).toList();

                if (messages.isEmpty) {
                  return const Center(child: Text('No messages yet. Start the conversation!', style: TextStyle(color: Colors.grey)));
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    final isMe = message['sender_id'] == myId;

                    return Align(
                      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        decoration: BoxDecoration(
                          color: isMe ? Theme.of(context).colorScheme.primary : Colors.grey[300],
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          message['message'],
                          style: TextStyle(color: isMe ? Colors.white : Colors.black87),
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -5))],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: Colors.grey[200],
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    backgroundColor: Theme.of(context).colorScheme.secondary,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
