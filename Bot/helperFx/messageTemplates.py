import emoji
from jinja2 import Template

####################################
######### DownLoading / Uploading ##
####################################
audio_item = Template(
    """
{{number}}  <strong>Title:</strong> {{Title}}
    <strong>Author:</strong> {{Author}}

"""
)


download_template = Template(
    """
{% if state == True %}
<strong>Downloading  <code>{{name}}</code></strong>{{emoji}}
{% else %}
<strong>Download Complete  <code>{{name}}</code></strong>{{emoji}}
{% endif %}
"""
)

uploading_template = Template(
    """
{% if state == True %}
<strong>Uploading {{title}}</strong>
<strong>Size:</strong><code>{{current}} / {{total}}</code>
<strong>Speed: {{speed}} &#x2B06;</strong>
<code> {{animation}} </code>
<i>ETA: {{eta}}</i>
{% else %}
<strong>Upload Complete  <code>{{title}}</code></strong>{{emoji}}
{% endif %}
"""
)

####################################
######### Greeting #################
####################################

greeting_template = Template(
    """
<strong>Howdy, <b>{{user_name}}</b> ! 👋🏻</strong>
I'm {{bot_name}} and I can send you audiobooks 📚🎧
Just type the name of the author or book and I'll check If it's available🤗. Here is quick search
"""
)


####################################
######### Post #####################
####################################
post_template = Template(
    """
<center><strong>{{title}}</strong></center> 📚🎧

Authors: {%for author in authors %} <strong>{{author}}</strong>{% endfor %}
{% if genres %}
<b>Genres:</b>
{%for line in genres %} 
<code>  -{{line}}</code> {% endfor %} {% endif %}
"""
)
