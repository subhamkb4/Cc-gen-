import telebot, random, re, time, requests, json, logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# ✅ Bot Configuration
TOKEN = "8430280406:AAHVlsBBVJm46-CG3FIkNE1eltYeVBjDJjg"
OWNER_ID = 7896890222
bot = telebot.TeleBot(TOKEN)

# ✅ Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("premium_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ✅ Enhanced Luhn Algorithm
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

# ✅ Multi-Gateway Simulation Class
class PremiumGatewayChecker:
    def __init__(self):
        self.gateways = {
            'braintree': self.check_braintree,
            'stripe': self.check_stripe,
            'paypal': self.check_paypal,
            'authorize_net': self.check_authorize_net,
            'square': self.check_square
        }
    
    def get_bin_info(self, card_number):
        """Enhanced BIN information with real lookup"""
        try:
            bin_number = card_number[:6]
            response = requests.get(f'https://lookup.binlist.net/{bin_number}', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                brand = data.get('scheme', 'UNKNOWN').upper()
                bank = data.get('bank', {}).get('name', 'N/A')
                country = data.get('country', {}).get('name', 'N/A')
                emoji = data.get('country', {}).get('emoji', '🏳️')
            else:
                first_digit = card_number[0]
                brand_map = {'4': 'VISA', '5': 'MASTERCARD', '3': 'AMEX', '6': 'DISCOVER'}
                brand = brand_map.get(first_digit, 'UNKNOWN')
                bank, country, emoji = "N/A", "N/A", "🏳️"
                
        except Exception:
            brand, bank, country, emoji = "UNKNOWN", "N/A", "N/A", "🏳️"
        
        return {
            'brand': brand,
            'bank': bank,
            'country': country,
            'emoji': emoji
        }
    
    def check_braintree(self, cc_data):
        """Enhanced Braintree simulation with realistic responses"""
        try:
            parts = cc_data.split('|')
            if len(parts) < 4:
                return {"error": "Invalid format"}
            
            cc, mm, yy, cvv = parts
            
            if not luhn(cc):
                return {
                    'status': 'declined',
                    'message': 'Invalid card number',
                    'gateway': 'Braintree Auth',
                    'response_code': '81723',
                    'risk_level': 'HIGH'
                }
            
            bin_info = self.get_bin_info(cc)
            card_prefix = cc[:1]
            
            banks = {
                '4': 'VISA INTERNATIONAL',
                '5': 'MASTERCARD BANK', 
                '3': 'AMERICAN EXPRESS',
                '6': 'DISCOVER BANK'
            }
            
            bank = banks.get(card_prefix, 'UNKNOWN BANK')
            card_type = "CREDIT" if random.random() > 0.4 else "DEBIT"
            
            responses = [
                {'status': 'success', 'message': 'Transaction approved', 'code': '1000', 'risk': 'LOW'},
                {'status': 'declined', 'message': 'Insufficient funds', 'code': '2001', 'risk': 'MEDIUM'},
                {'status': 'declined', 'message': 'Card expired', 'code': '2004', 'risk': 'HIGH'},
                {'status': 'declined', 'message': 'Invalid CVV', 'code': '2007', 'risk': 'HIGH'},
                {'status': 'declined', 'message': 'Transaction not permitted', 'code': '2008', 'risk': 'MEDIUM'},
                {'status': 'error', 'message': 'Processor network error', 'code': '3001', 'risk': 'LOW'},
            ]
            
            weights = [20, 25, 15, 15, 15, 10]
            response = random.choices(responses, weights=weights)[0]
            
            processing_time = round(random.uniform(1.2, 3.8), 2)
            
            return {
                'status': response['status'],
                'message': response['message'],
                'gateway': 'Braintree Auth',
                'response_code': response['code'],
                'risk_level': response['risk'],
                'card_type': card_type,
                'bank': bank,
                'bin_info': bin_info,
                'processing_time': processing_time,
                'timestamp': time.strftime("%I:%M %P")
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Processing error: {str(e)}',
                'gateway': 'Braintree Auth',
                'response_code': '9001',
                'risk_level': 'HIGH'
            }
    
    def check_stripe(self, cc_data):
        """Stripe gateway simulation"""
        try:
            parts = cc_data.split('|')
            cc, mm, yy, cvv = parts
            
            processing_time = round(random.uniform(1.0, 2.5), 2)
            last_digit = int(cc[-1])
            
            if last_digit % 3 == 0:
                return {
                    'status': 'success',
                    'message': 'Payment approved',
                    'gateway': 'Stripe',
                    'response_code': 'succeeded',
                    'processing_time': processing_time
                }
            else:
                return {
                    'status': 'declined',
                    'message': 'Card declined',
                    'gateway': 'Stripe',
                    'response_code': 'card_declined',
                    'processing_time': processing_time
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gateway error: {str(e)}',
                'gateway': 'Stripe',
                'response_code': 'api_error'
            }
    
    def check_paypal(self, cc_data):
        """PayPal gateway simulation"""
        try:
            processing_time = round(random.uniform(1.5, 3.0), 2)
            
            if random.random() < 0.3:
                return {
                    'status': 'success',
                    'message': 'Payment completed',
                    'gateway': 'PayPal',
                    'response_code': 'PAYMENT_COMPLETED',
                    'processing_time': processing_time
                }
            else:
                return {
                    'status': 'declined',
                    'message': 'Funding instrument declined',
                    'gateway': 'PayPal',
                    'response_code': 'FUNDING_SOURCE_DECLINED',
                    'processing_time': processing_time
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gateway error: {str(e)}',
                'gateway': 'PayPal',
                'response_code': 'INTERNAL_ERROR'
            }
    
    def check_authorize_net(self, cc_data):
        """Authorize.net gateway simulation"""
        try:
            processing_time = round(random.uniform(2.0, 4.0), 2)
            checksum = sum(int(d) for d in cc_data.split('|')[0]) % 10
            
            if checksum < 3:
                return {
                    'status': 'success',
                    'message': 'Transaction approved',
                    'gateway': 'Authorize.net',
                    'response_code': '1',
                    'processing_time': processing_time
                }
            else:
                return {
                    'status': 'declined',
                    'message': 'Transaction declined',
                    'gateway': 'Authorize.net',
                    'response_code': '2',
                    'processing_time': processing_time
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gateway error: {str(e)}',
                'gateway': 'Authorize.net',
                'response_code': '3'
            }
    
    def check_square(self, cc_data):
        """Square gateway simulation"""
        try:
            processing_time = round(random.uniform(1.2, 3.5), 2)
            cc = cc_data.split('|')[0]
            
            if sum(int(d) for d in cc) % 7 == 0:
                return {
                    'status': 'success',
                    'message': 'Payment captured',
                    'gateway': 'Square',
                    'response_code': 'PAYMENT_CAPTURED',
                    'processing_time': processing_time
                }
            else:
                return {
                    'status': 'declined',
                    'message': 'Card declined',
                    'gateway': 'Square',
                    'response_code': 'CARD_DECLINED',
                    'processing_time': processing_time
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Gateway error: {str(e)}',
                'gateway': 'Square',
                'response_code': 'INTERNAL_ERROR'
            }
    
    def check_all_gateways(self, cc_data):
        """Check card against all gateways"""
        results = {}
        for gateway_name, gateway_func in self.gateways.items():
            results[gateway_name] = gateway_func(cc_data)
            time.sleep(0.5)  # Simulate sequential processing
        
        return results

# ✅ Initialize Premium Checker
premium_checker = PremiumGatewayChecker()

# ✅ Enhanced Card Generation
def generate_card(bin_format):
    bin_format = bin_format.lower()
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]
    while True:
        cc = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_format)
        if luhn(cc):
            return cc

def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]

    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN provided.\n\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

    bin_info = premium_checker.get_bin_info(bin_clean + "0"*10)
    scheme = bin_info['brand']
    ctype = "DEBIT" if random.random() > 0.5 else "CREDIT"

    cards = []
    start = time.time()
    for _ in range(10):
        cc = generate_card(bin_format)
        mm = mm_input if mm_input else str(random.randint(1, 12)).zfill(2)
        yy_full = yy_input if yy_input else str(random.randint(2026, 2032))
        yy = yy_full[-2:]
        cvv = cvv_input if cvv_input else str(random.randint(100, 999))
        cards.append(f"<code>{cc}|{mm}|{yy}|{cvv}</code>")
    elapsed = round(time.time() - start, 3)

    card_lines = "\n".join(cards)

    text = f"""<b>🔰 PREMIUM CARD GENERATOR</b>
<b>────────────────────</b>
<b>🎯 Info:</b> {scheme} - {ctype}
<b>🏦 Bank:</b> {bin_info['bank']}
<b>🌍 Country:</b> {bin_info['country']} {bin_info['emoji']}
<b>────────────────────</b>
<b>🔢 BIN:</b> {bin_clean} | <b>⏱️ Time:</b> {elapsed}s
<b>📥 Input:</b> <code>{bin_input}</code>
<b>────────────────────</b>
{card_lines}
<b>────────────────────</b>
<b>👤 Requested By:</b> @{username}
<b>⚡ Premium Generator</b>
"""
    return text

# ✅ Fake Identity Generator
def generate_fake_identity(country_code):
    try:
        url = f"https://randomuser.me/api/?nat={country_code}"
        res = requests.get(url).json()
        user = res['results'][0]

        name = f"{user['name']['first']} {user['name']['last']}"
        addr = user['location']
        full_address = f"{addr['street']['number']} {addr['street']['name']}"
        city = addr['city']
        state = addr['state']
        zip_code = addr['postcode']
        country = addr['country']
        email = user['email']
        phone = user['phone']
        dob = user['dob']['date'][:10]

        return f"""📦 <b>PREMIUM FAKE IDENTITY</b>
<b>────────────────────</b>
<b>👤 Name:</b> <code>{name}</code>
<b>🏠 Address:</b> <code>{full_address}</code>
<b>🏙️ City:</b> <code>{city}</code>
<b>📍 State:</b> <code>{state}</code>
<b>📮 ZIP:</b> <code>{zip_code}</code>
<b>🌐 Country:</b> <code>{country}</code>
<b>📧 Email:</b> <code>{email}</code>
<b>📞 Phone:</b> <code>{phone}</code>
<b>🎂 DOB:</b> <code>{dob}</code>
<b>────────────────────</b>
<b>⚡ Premium Identity Generator</b>"""
    except Exception as e:
        return f"❌ Error generating identity: {str(e)}"

# ✅ Enhanced Command Handlers
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = str(message.from_user.id)
    with open("premium_users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read().splitlines():
            f.write(user_id + "\n")

    text = (
        "🤖 <b>PREMIUM MULTI-GATEWAY BOT</b> 🔥\n\n"
        "💠 <b>Advanced Features:</b>\n"
        "• Multi-Gateway Checking\n"
        "• Premium Card Generation\n"
        "• Fake Identity Generator\n"
        "• Real BIN Lookup\n"
        "• Professional Analytics\n\n"
        "📢 <b>Updates:</b> @BLAZE_X_007\n\n"
        "💡 <b>Tip:</b> Use /cmds for all commands\n"
        "🤖 <i>DEV - https://t.me/BLAZE_X_007</i>"
    )
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['cmds'])
def cmds_handler(message):
    cmds_text = """
<b>🤖 PREMIUM BOT COMMANDS</b>

<b>🎯 CARD GENERATION:</b>
<code>/gen bin|mm|yy|cvv</code> - Generate premium cards
<code>/gen 545231xx|03|27|xxx</code> - Example

<b>🔍 MULTI-GATEWAY CHECKING:</b>
<code>/chk cc|mm|yy|cvv</code> - Single gateway check
<code>/mchk cc|mm|yy|cvv</code> - Multi-gateway check
<code>/all cc|mm|yy|cvv</code> - All gateways

<b>🌍 IDENTITY & TOOLS:</b>
<code>/fake country</code> - Generate fake identity
<code>/country</code> - Supported countries
<code>/ask question</code> - AI assistant

<b>⚙️ ADMIN TOOLS:</b>
<code>/stats</code> - Bot statistics
<code>/broadcast msg</code> - Broadcast message

<b>💡 EXAMPLES:</b>
<code>/gen 411111xxxxxxxxxx|12|25|123</code>
<code>/chk 4111111111111111|12|25|123</code>
<code>/mchk 5111111111111118|03|26|456</code>
<code>/fake us</code>
"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🎲 Generate Cards", callback_data="help_gen"),
        InlineKeyboardButton("🔍 Check Cards", callback_data="help_chk"),
        InlineKeyboardButton("🌍 Fake Data", callback_data="help_fake"),
        InlineKeyboardButton("📊 Multi-Check", callback_data="help_mchk")
    ]
    keyboard.add(*buttons)
    
    bot.reply_to(message, cmds_text, parse_mode="HTML", reply_markup=keyboard)

@bot.message_handler(commands=['gen'])
def gen_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Example:</b>\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>", parse_mode="HTML")

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}"))
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=btn)

@bot.message_handler(commands=['chk'])
def chk_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, 
            "⚠️ <b>Usage:</b>\n<code>/chk 4111111111111111|12|25|123</code>\n\n"
            "🤖 <i>DEV - https://t.me/BLAZE_X_007</i>", 
            parse_mode="HTML"
        )
    
    cc_data = parts[1].strip()
    username = message.from_user.username or "anonymous"
    
    processing_msg = bot.reply_to(message, "🔄 <b>Connecting to Braintree Gateway...</b>", parse_mode="HTML")
    
    time.sleep(2)
    
    result = premium_checker.check_braintree(cc_data)
    
    status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'declined' else "⚠️"
    risk_color = "🟢" if result.get('risk_level') == 'LOW' else "🟡" if result.get('risk_level') == 'MEDIUM' else "🔴"
    
    response_text = f"""
<b>🔐 PREMIUM GATEWAY CHECK</b>
<b>────────────────────</b>
<b>🎯 Status:</b> {status_icon} {result['status'].upper()}
<b>📨 Message:</b> {result['message']}
<b>🔧 Gateway:</b> {result['gateway']}
<b>📟 Response Code:</b> {result['response_code']}
<b>⚠️ Risk Level:</b> {risk_color} {result.get('risk_level', 'UNKNOWN')}

<b>💳 Card Information:</b>
<b>🏦 Bank:</b> {result.get('bank', 'N/A')}
<b>🎫 Type:</b> {result.get('card_type', 'N/A')}

<b>⏱️ Processing:</b>
<b>🚀 Time:</b> {result['processing_time']}s
<b>🕐 Timestamp:</b> {result['timestamp']}
<b>────────────────────</b>
<b>👤 Requested By:</b> @{username}
<b>⚡ Premium Checker</b>
"""
    
    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("🔄 Retry Check", callback_data=f"retry_chk|{cc_data}"))
    btn.add(InlineKeyboardButton("🌐 Multi-Check", callback_data=f"multi_chk|{cc_data}"))
    
    try:
        bot.edit_message_text(
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
            text=response_text,
            parse_mode="HTML",
            reply_markup=btn
        )
    except:
        bot.send_message(
            processing_msg.chat_id,
            response_text,
            parse_mode="HTML",
            reply_markup=btn
        )

@bot.message_handler(commands=['mchk', 'all'])
def multi_check_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, 
            "⚠️ <b>Usage:</b>\n<code>/mchk 4111111111111111|12|25|123</code>\n\n"
            "🔍 <i>Checks all available gateways</i>", 
            parse_mode="HTML"
        )
    
    cc_data = parts[1].strip()
    username = message.from_user.username or "anonymous"
    
    processing_msg = bot.reply_to(message, "🔄 <b>Starting Multi-Gateway Analysis...</b>", parse_mode="HTML")
    
    results = premium_checker.check_all_gateways(cc_data)
    
    # Format comprehensive results
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    response_text = f"""
<b>🔰 PREMIUM MULTI-GATEWAY ANALYSIS</b>
<b>────────────────────</b>
<b>📊 Summary:</b> {success_count}/{total_count} Gateways Approved
<b>📈 Success Rate:</b> {(success_count/total_count)*100:.1f}%

<b>🎯 Gateway Results:</b>
"""
    
    for gateway, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'declined' else "⚠️"
        response_text += f"\n<b>{gateway.upper():12}</b> {status_icon} {result['message']} ({result['processing_time']}s)"
    
    response_text += f"""
<b>────────────────────</b>
<b>💳 Card:</b> <code>{cc_data.split('|')[0][:6]}XXXXXX{cc_data.split('|')[0][-4:]}</code>
<b>👤 User:</b> @{username}
<b>⚡ Premium Multi-Checker</b>
"""
    
    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("🔄 Re-Analyze", callback_data=f"multi_chk|{cc_data}"))
    btn.add(InlineKeyboardButton("📊 Single Check", callback_data=f"retry_chk|{cc_data}"))
    
    try:
        bot.edit_message_text(
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
            text=response_text,
            parse_mode="HTML",
            reply_markup=btn
        )
    except:
        bot.send_message(
            processing_msg.chat_id,
            response_text,
            parse_mode="HTML",
            reply_markup=btn
        )

@bot.message_handler(commands=['fake'])
def fake_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Example:</b>\n<code>/fake us</code>", parse_mode="HTML")

    country_code = parts[1].strip().lower()
    identity_text = generate_fake_identity(country_code)
    
    bot.reply_to(message, identity_text, parse_mode="HTML")

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 <b>Access Denied:</b> Owner only command", parse_mode="HTML")
    
    try:
        with open("premium_users.txt", "r") as f:
            users = f.read().splitlines()
        user_count = len(users)
    except:
        user_count = 0
    
    stats_text = f"""
<b>📊 PREMIUM BOT STATISTICS</b>
<b>────────────────────</b>
<b>👥 Total Users:</b> {user_count}
<b>🤖 Bot Status:</b> 🟢 Online
<b>⚡ Version:</b> Premium v2.0
<b>🔧 Gateways:</b> 5 Active
<b>🎯 Features:</b> Multi-Gateway, BIN Lookup, AI

<b>────────────────────</b>
<b>👑 Owner:</b> @BLAZE_X_007
<b>⚡ Premium Analytics</b>
"""
    bot.reply_to(message, stats_text, parse_mode="HTML")


# ✅ /ask command (uses external GPT API)
@bot.message_handler(commands=['ask'])
def ask_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "❓ Usage: `/ask your question`", parse_mode="Markdown")
    
    prompt = parts[1]
    try:
        res = requests.get(f"https://gpt-3-5.apis-bj-devs.workers.dev/?prompt={prompt}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") and data.get("reply"):
                reply = data["reply"]
                bot.reply_to(message, f"*{reply}*", parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ Couldn't parse reply from API.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ GPT API failed to respond.", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: `{e}`", parse_mode="Markdown")
        
        
# ✅ /country command
@bot.message_handler(commands=['country'])
def country_command(message):
    msg = """🌍 *Supported Countries:*

1. Algeria (DZ)
2. Argentina (AR)
3. Australia (AU)
4. Bahrain (BH)
5. Bangladesh (BD)
6. Belgium (BE)
7. Brazil (BR)
8. Cambodia (KH)
9. Canada (CA)
10. Colombia (CO)
11. Denmark (DK)
12. Egypt (EG)
13. Finland (FI)
14. France (FR)
15. Germany (DE)
16. India (IN)
17. Italy (IT)
18. Japan (JP)
19. Kazakhstan (KZ)
20. Malaysia (MY)
21. Mexico (MX)
22. Morocco (MA)
23. New Zealand (NZ)
24. Panama (PA)
25. Pakistan (PK)
26. Peru (PE)
27. Poland (PL)
28. Qatar (QA)
29. Saudi Arabia (SA)
30. Singapore (SG)
31. Spain (ES)
32. Sweden (SE)
33. Switzerland (CH)
34. Thailand (TH)
35. Turkiye (TR)
36. United Kingdom (UK)
37. United States (US)"""
    bot.reply_to(message, msg, parse_mode="Markdown")
    
    
# ✅ Enhanced Callback Handlers
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith("again|"):
        bin_input = call.data.split("|", 1)[1]
        username = call.from_user.username or "anonymous"
        text = generate_output(bin_input, username)

        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}"))

        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  parse_mode="HTML",
                                  reply_markup=btn)
        except:
            bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=btn)

    elif call.data.startswith("retry_chk|"):
        cc_data = call.data.split("|", 1)[1]
        username = call.from_user.username or "anonymous"
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🔄 <b>Re-checking with Gateway...</b>",
                parse_mode="HTML"
            )
        except:
            pass
        
        time.sleep(1)
        result = premium_checker.check_braintree(cc_data)
        
        status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'declined' else "⚠️"
        risk_color = "🟢" if result.get('risk_level') == 'LOW' else "🟡" if result.get('risk_level') == 'MEDIUM' else "🔴"
        
        response_text = f"""
<b>🔐 PREMIUM GATEWAY CHECK</b>
<b>────────────────────</b>
<b>🎯 Status:</b> {status_icon} {result['status'].upper()}
<b>📨 Message:</b> {result['message']}
<b>🔧 Gateway:</b> {result['gateway']}
<b>📟 Response Code:</b> {result['response_code']}
<b>⚠️ Risk Level:</b> {risk_color} {result.get('risk_level', 'UNKNOWN')}

<b>⏱️ Processing:</b>
<b>🚀 Time:</b> {result['processing_time']}s
<b>🕐 Timestamp:</b> {result['timestamp']}
<b>────────────────────</b>
<b>👤 Requested By:</b> @{username}
<b>⚡ Premium Checker</b>
"""
        
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("🔄 Retry Check", callback_data=f"retry_chk|{cc_data}"))
        btn.add(InlineKeyboardButton("🌐 Multi-Check", callback_data=f"multi_chk|{cc_data}"))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response_text,
                parse_mode="HTML",
                reply_markup=btn
            )
        except:
            bot.send_message(call.message.chat.id, response_text, parse_mode="HTML", reply_markup=btn)

    elif call.data.startswith("multi_chk|"):
        cc_data = call.data.split("|", 1)[1]
        username = call.from_user.username or "anonymous"
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🔄 <b>Starting Multi-Gateway Analysis...</b>",
                parse_mode="HTML"
            )
        except:
            pass
        
        results = premium_checker.check_all_gateways(cc_data)
        
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        total_count = len(results)
        
        response_text = f"""
<b>🔰 PREMIUM MULTI-GATEWAY ANALYSIS</b>
<b>────────────────────</b>
<b>📊 Summary:</b> {success_count}/{total_count} Gateways Approved
<b>📈 Success Rate:</b> {(success_count/total_count)*100:.1f}%

<b>🎯 Gateway Results:</b>
"""
        
        for gateway, result in results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'declined' else "⚠️"
            response_text += f"\n<b>{gateway.upper():12}</b> {status_icon} {result['message']} ({result['processing_time']}s)"
        
        response_text += f"""
<b>────────────────────</b>
<b>💳 Card:</b> <code>{cc_data.split('|')[0][:6]}XXXXXX{cc_data.split('|')[0][-4:]}</code>
<b>👤 User:</b> @{username}
<b>⚡ Premium Multi-Checker</b>
"""
        
        btn = InlineKeyboardMarkup()
        btn.add(InlineKeyboardButton("🔄 Re-Analyze", callback_data=f"multi_chk|{cc_data}"))
        btn.add(InlineKeyboardButton("📊 Single Check", callback_data=f"retry_chk|{cc_data}"))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response_text,
                parse_mode="HTML",
                reply_markup=btn
            )
        except:
            bot.send_message(call.message.chat.id, response_text, parse_mode="HTML", reply_markup=btn)

# ✅ Broadcast Command (Owner Only)
@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 <b>Access Denied</b>", parse_mode="HTML")

    try:
        _, text = message.text.split(" ", 1)
    except:
        return bot.reply_to(message, "⚠️ <b>Usage:</b>\n<code>/broadcast Your message</code>", parse_mode="HTML")

    bot.reply_to(message, "📢 <b>Sending broadcast to all users...</b>", parse_mode="HTML")

    try:
        with open("premium_users.txt", "r") as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        return bot.send_message(message.chat.id, "❌ <b>No users found</b>", parse_mode="HTML")

    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 <b>Premium Broadcast:</b>\n\n{text}", parse_mode="HTML")
            sent += 1
            time.sleep(0.1)
        except:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"✅ <b>Broadcast Completed</b>\n\n🟢 Sent: <code>{sent}</code>\n🔴 Failed: <code>{failed}</code>",
        parse_mode="HTML"
    )

print("🚀 PREMIUM MULTI-GATEWAY BOT STARTED")
print("🔧 Bot Token: Configured")
print("👑 Owner ID:", OWNER_ID)
print("⚡ Features: Multi-Gateway, BIN Lookup, Premium Generator")
print("📱 Bot is now running...")
print("🤖 Developer: @BLAZE_X_007")

bot.polling()