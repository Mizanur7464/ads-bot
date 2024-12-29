import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

# বট টোকেন
TOKEN = '7954357634:AAEJdjBMyD2aUFL-eBcpCr8Drt5ZnyoPn8M'
bot = telebot.TeleBot(TOKEN)

ads_content = {}
# SQLite ডাটাবেস সংযোগ এবং টেবিল তৈরি
conn = sqlite3.connect('ads.db', check_same_thread=False)
cursor = conn.cursor()

# টেবিল তৈরি (এড স্টোর করার জন্য)
cursor.execute('''
CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ad_text TEXT,
    ad_media TEXT
)
''')

# Start কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    
    # বাটন তৈরি
    create_ad_button = InlineKeyboardButton("Create Ad", callback_data="create_ad")
    edit_ad_button = InlineKeyboardButton("Edit Ad", callback_data="edit_ad")
    show_ad_button = InlineKeyboardButton("Show Ad", callback_data="show_ad")
    customization_button = InlineKeyboardButton("A Customization", callback_data="customization")
    send_ad_button = InlineKeyboardButton("Send Ad", callback_data="send_ad")
    
    # বাটনগুলো markup এ অ্যাড করা
    markup.add(create_ad_button, edit_ad_button, show_ad_button, customization_button, send_ad_button)

    # মেসেজ পাঠানো
    bot.send_message(message.chat.id, "Welcome Admin! Choose an option:", reply_markup=markup)

# "Create Ad" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "create_ad")
def create_ad(call):
    bot.send_message(call.message.chat.id, "Send me your ad text:")

# প্রথম টেক্সট ইনপুট হ্যান্ডলার
@bot.message_handler(func=lambda message: message.chat.id not in ads_content)
def handle_ad_text(message):
    # টেক্সট স্টোর করা
    ads_content[message.chat.id] = {'text': message.text, 'media': None}
    bot.send_message(message.chat.id, "Ad text added! Now, send me your campaign image or logo:")

# ছবি বা ভিডিও আপলোড করার জন্য হ্যান্ডলার
@bot.message_handler(content_types=['photo', 'video'])
def handle_ad_media(message):
    if message.content_type == 'photo':
        # ইমেজ স্টোর করা
        ads_content[message.chat.id]['media'] = message.photo[-1].file_id
        # বিজ্ঞাপন স্বয়ংক্রিয়ভাবে তৈরি
        ad_text = ads_content[message.chat.id]['text']
        bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=ad_text)
        
        # ডাটাবেসে এড স্টোর করা
        cursor.execute('INSERT INTO ads (user_id, ad_text, ad_media) VALUES (?, ?, ?)', 
                       (message.chat.id, ad_text, message.photo[-1].file_id))
        conn.commit()
        
        # Success message with "Ad created successfully!" and Back button
        markup = InlineKeyboardMarkup()
        back_button = InlineKeyboardButton("Back", callback_data="back_to_home")
        markup.add(back_button)
        bot.send_message(message.chat.id, "Ad created successfully!", reply_markup=markup)
        
        # Clear ad data after creation
        ads_content[message.chat.id] = {}

    elif message.content_type == 'video':
        # ভিডিও স্টোর করা
        ads_content[message.chat.id]['media'] = message.video.file_id
        # বিজ্ঞাপন স্বয়ংক্রিয়ভাবে তৈরি
        ad_text = ads_content[message.chat.id]['text']
        bot.send_video(message.chat.id, message.video.file_id, caption=ad_text)
        
        # ডাটাবেসে এড স্টোর করা
        cursor.execute('INSERT INTO ads (user_id, ad_text, ad_media) VALUES (?, ?, ?)', 
                       (message.chat.id, ad_text, message.video.file_id))
        conn.commit()
        
        # Success message with "Ad created successfully!" and Back button
        markup = InlineKeyboardMarkup()
        back_button = InlineKeyboardButton("Back", callback_data="back_to_home")
        markup.add(back_button)
        bot.send_message(message.chat.id, "Ad created successfully!", reply_markup=markup)
        
        # Clear ad data after creation
        ads_content[message.chat.id] = {}

# "Edit Ad" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "edit_ad")
def edit_ad(call):
    # ডাটাবেস থেকে এড টানানো
    cursor.execute('SELECT * FROM ads WHERE user_id = ?', (call.message.chat.id,))
    ads = cursor.fetchall()
    
    if ads:
        # সব এড দেখানো
        for ad in ads:
            ad_text = ad[2]
            ad_media = ad[3]
            
            markup = InlineKeyboardMarkup()
            edit_button = InlineKeyboardButton("Edit", callback_data=f"edit_{ad[0]}")
            delete_button = InlineKeyboardButton("Delete", callback_data=f"delete_{ad[0]}")
            markup.add(edit_button, delete_button)
            
            if ad_media:
                bot.send_photo(call.message.chat.id, ad_media, caption=ad_text, reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, ad_text, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "No ads found to edit.")

# "Edit" বাটন ক্লিক করলে এডিট অপশন
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_ad_content(call):
    ad_id = call.data.split("_")[1]
    
    # ডাটাবেস থেকে পুরনো এডটি টানানো
    cursor.execute('SELECT * FROM ads WHERE id = ?', (ad_id,))
    ad = cursor.fetchone()

    if ad:
        bot.send_message(call.message.chat.id, f"Current Ad Text: {ad[2]}")
        bot.send_message(call.message.chat.id, "Send me the new ad text:")
        ads_content[call.message.chat.id] = {'ad_id': ad_id, 'text': ad[2], 'media': ad[3]}
    else:
        bot.send_message(call.message.chat.id, "Ad not found!")

# নতুন টেক্সট ইনপুট নেওয়া
@bot.message_handler(func=lambda message: message.chat.id in ads_content and 'ad_id' in ads_content[message.chat.id])
def update_ad_text(message):
    # নতুন টেক্সট আপডেট করা
    ads_content[message.chat.id]['text'] = message.text
    bot.send_message(message.chat.id, "Ad text updated! Now, send me the updated campaign image or logo:")

# ছবি বা ভিডিও আপলোড করার জন্য হ্যান্ডলার (এডিট করার জন্য)
@bot.message_handler(content_types=['photo', 'video'])
def update_ad_media(message):
    ad_id = ads_content[message.chat.id]['ad_id']
    new_text = ads_content[message.chat.id]['text']
    
    if message.content_type == 'photo':
        new_media = message.photo[-1].file_id
        cursor.execute('UPDATE ads SET ad_text = ?, ad_media = ? WHERE id = ?', 
                       (new_text, new_media, ad_id))
        conn.commit()
        
        bot.send_photo(message.chat.id, new_media, caption=new_text)
        bot.send_message(message.chat.id, "Ad updated successfully!")
        
    elif message.content_type == 'video':
        new_media = message.video.file_id
        cursor.execute('UPDATE ads SET ad_text = ?, ad_media = ? WHERE id = ?', 
                       (new_text, new_media, ad_id))
        conn.commit()
        
        bot.send_video(message.chat.id, new_media, caption=new_text)
        bot.send_message(message.chat.id, "Ad updated successfully!")

    # Clear ad data after update
    ads_content[message.chat.id] = {}

# "Delete" বাটন ক্লিক করলে ডিলিট করা হবে
@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_ad(call):
    ad_id = call.data.split("_")[1]
    cursor.execute('DELETE FROM ads WHERE id = ?', (ad_id,))
    conn.commit()
    bot.send_message(call.message.chat.id, "Ad deleted successfully.")

# "Back" বাটন ক্লিক করলে হোম পেজে ফিরে যাবে
@bot.callback_query_handler(func=lambda call: call.data == "back_to_home")
def back_to_home(call):
    markup = InlineKeyboardMarkup()
    
    # বাটন তৈরি
    create_ad_button = InlineKeyboardButton("Create Ad", callback_data="create_ad")
    edit_ad_button = InlineKeyboardButton("Edit Ad", callback_data="edit_ad")
    show_ad_button = InlineKeyboardButton("Show Ad", callback_data="show_ad")
    customization_button = InlineKeyboardButton("A Customization", callback_data="customization")
    send_ad_button = InlineKeyboardButton("Send Ad", callback_data="send_ad")
    
    # বাটনগুলো markup এ অ্যাড করা
    markup.add(create_ad_button, edit_ad_button, show_ad_button, customization_button, send_ad_button)

    # হোম পেজে ফিরে যাওয়ার মেসেজ
    bot.send_message(call.message.chat.id, "Welcome Admin! Choose an option:", reply_markup=markup)
# "Show Ad" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "show_ad")
def show_ads(call):
    # ডাটাবেস থেকে বিজ্ঞাপনগুলো টানানো
    cursor.execute('SELECT * FROM ads WHERE user_id = ?', (call.message.chat.id,))
    ads = cursor.fetchall()

    if ads:
        # সব বিজ্ঞাপন দেখানো
        for ad in ads:
            ad_text = ad[2]
            ad_media = ad[3]
            
            # Inline বাটন তৈরি করা
            markup = InlineKeyboardMarkup()
            forward_button = InlineKeyboardButton("Forward", callback_data=f"forward_{ad[0]}")
            markup.add(forward_button)
            
            # মিডিয়া সহ বিজ্ঞাপন প্রদর্শন
            if ad_media:
                bot.send_photo(call.message.chat.id, ad_media, caption=ad_text, reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, ad_text, reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "No ads found to show.")

# "A customization" অপশনের জন্য হ্যান্ডলার
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# "A customization" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "customization")
def a_customization(call):
    markup = InlineKeyboardMarkup()

    # বাটনের সংখ্যা সেট করার জন্য
    buttons_count_button = InlineKeyboardButton("Set Buttons Count", callback_data="set_buttons_count")
    markup.add(buttons_count_button)

    # লেআউট কাস্টমাইজেশন
    layout_button = InlineKeyboardButton("Set Layout", callback_data="set_layout")
    markup.add(layout_button)

    # অর্ডার কাস্টমাইজেশন
    order_button = InlineKeyboardButton("Set Order", callback_data="set_order")
    markup.add(order_button)

    bot.send_message(call.message.chat.id, "Choose a customization option:", reply_markup=markup)

# "Set Layout" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "set_layout")
def set_layout(call):
    # লেআউট পছন্দের ইনলাইন কীবোর্ড তৈরি
    markup = InlineKeyboardMarkup()
    grid_button = InlineKeyboardButton("Grid Layout", callback_data="grid")
    list_button = InlineKeyboardButton("List Layout", callback_data="list")
    horizontal_button = InlineKeyboardButton("Horizontal Layout", callback_data="horizontal")
    
    markup.add(grid_button, list_button, horizontal_button)

    bot.send_message(call.message.chat.id, "Choose the layout style (Grid, List, Horizontal):", reply_markup=markup)

# "Grid Layout" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "grid")
def grid_layout(call):
    bot.send_message(call.message.chat.id, "You have selected 'Grid' layout. Your ads will be displayed in a grid format.")
    # এখানে আপনি গ্রিড লেআউটের জন্য কোড যুক্ত করতে পারবেন

# "List Layout" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "list")
def list_layout(call):
    bot.send_message(call.message.chat.id, "You have selected 'List' layout. Your ads will be displayed in a list format.")
    # এখানে আপনি লিস্ট লেআউটের জন্য কোড যুক্ত করতে পারবেন

# "Horizontal Layout" অপশনের জন্য হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "horizontal")
def horizontal_layout(call):
    bot.send_message(call.message.chat.id, "You have selected 'Horizontal' layout. Your ads will be displayed in a horizontal format.")
    # এখানে আপনি হরিজেন্টাল লেআউটের জন্য কোড যুক্ত করতে পারবেন

# বট চালানো
bot.polling()
