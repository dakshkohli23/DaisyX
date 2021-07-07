# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2021 Nico Robin

# This file is part of Daisy (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import html
import random

import bs4
import jikanpy
import requests
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters

from DaisyX.decorator import register
from DaisyX.services.pyrogram import pbot

from .utils.anime import (
    airing_query,
    anime_query,
    character_query,
    manga_query,
    shorten,
    t,
)
from .utils.disable import disableable_dec

url = "https://graphql.anilist.co"


@register(cmds="airing")
@disableable_dec("airing")
async def anime_airing(message):
    search_str = message.text.split(" ", 1)
    if len(search_str) == 1:
        await message.reply("Provide anime name!")
        return

    variables = {"search": search_str[1]}
    response = requests.post(
        url, json={"query": airing_query, "variables": variables}
    ).json()["data"]["Media"]
    ms_g = f"<b>Name</b>: <b>{response['title']['romaji']}</b>(<code>{response['title']['native']}</code>)\n<b>ID</b>: <code>{response['id']}</code>"
    if response["nextAiringEpisode"]:
        airing_time = response["nextAiringEpisode"]["timeUntilAiring"] * 1000
        airing_time_final = t(airing_time)
        ms_g += f"\n<b>Episode</b>: <code>{response['nextAiringEpisode']['episode']}</code>\n<b>Airing In</b>: <code>{airing_time_final}</code>"
    else:
        ms_g += f"\n<b>Episode</b>: <code>{response['episodes']}</code>\n<b>Status</b>: <code>N/A</code>"
    await message.reply(ms_g)


@register(cmds="anime")
@disableable_dec("anime")
async def anime_search(message):
    search = message.text.split(" ", 1)
    if len(search) == 1:
        await message.reply("Provide anime name!")
        return
    else:
        search = search[1]
    variables = {"search": search}
    json = (
        requests.post(url, json={"query": anime_query, "variables": variables})
        .json()["data"]
        .get("Media", None)
    )
    if json:
        msg = f"<b>{json['title']['romaji']}</b>(<code>{json['title']['native']}</code>)\n<b>Type</b>: {json['format']}\n<b>Status</b>: {json['status']}\n<b>Episodes</b>: {json.get('episodes', 'N/A')}\n<b>Duration</b>: {json.get('duration', 'N/A')} Per Ep.\n<b>Score</b>: {json['averageScore']}\n<b>Genres</b>: <code>"
        for x in json["genres"]:
            msg += f"{x}, "
        msg = msg[:-2] + "</code>\n"
        msg += "<b>Studios</b>: <code>"
        for x in json["studios"]["nodes"]:
            msg += f"{x['name']}, "
        msg = msg[:-2] + "</code>\n"
        info = json.get("siteUrl")
        trailer = json.get("trailer", None)
        if trailer:
            trailer_id = trailer.get("id", None)
            site = trailer.get("site", None)
            if site == "youtube":
                trailer = "https://youtu.be/" + trailer_id
        description = (
            json.get("description", "N/A")
            .replace("<i>", "")
            .replace("</i>", "")
            .replace("<br>", "")
        )
        msg += shorten(description, info)
        image = info.replace("anilist.co/anime/", "img.anili.st/media/")
        if trailer:
            buttons = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="More Info", url=info),
                InlineKeyboardButton(text="🎬 Trailer", url=trailer),
            )
        else:
            buttons = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="More Info", url=info)
            )

        if image:
            try:
                await message.reply_photo(image, caption=msg, reply_markup=buttons)
            except:
                msg += f" [〽️]({image})"
                await message.reply(msg)
        else:
            await message.reply(msg)


@register(cmds="character")
@disableable_dec("character")
async def character_search(message):
    search = message.text.split(" ", 1)
    if len(search) == 1:
        await message.reply("Provide character name!")
        return
    search = search[1]
    variables = {"query": search}
    json = (
        requests.post(url, json={"query": character_query, "variables": variables})
        .json()["data"]
        .get("Character")
    )
    if json:
        ms_g = f"<b>{json.get('name').get('full')}</b>(<code>{json.get('name').get('native')}</code>)\n"
        description = (f"{json['description']}").replace("__", "")
        site_url = json.get("siteUrl")
        ms_g += shorten(description, site_url)
        image = json.get("image", None)
        if image:
            image = image.get("large")
            await message.reply_photo(image, caption=ms_g)
        else:
            await message.reply(ms_g)


@register(cmds="manga")
@disableable_dec("manga")
async def manga_search(message):
    search = message.text.split(" ", 1)
    if len(search) == 1:
        await message.reply("Provide manga name!")
        return
    search = search[1]
    variables = {"search": search}
    json = (
        requests.post(url, json={"query": manga_query, "variables": variables})
        .json()["data"]
        .get("Media", None)
    )
    ms_g = ""
    if json:
        title, title_native = json["title"].get("romaji", False), json["title"].get(
            "native", False
        )
        start_date, status, score = (
            json["startDate"].get("year", False),
            json.get("status", False),
            json.get("averageScore", False),
        )
        if title:
            ms_g += f"<b>{title}</b>"
            if title_native:
                ms_g += f"(<code>{title_native}</code>)"
        if start_date:
            ms_g += f"\n<b>Start Date</b> - <code>{start_date}</code>"
        if status:
            ms_g += f"\n<b>Status</b> - <code>{status}</code>"
        if score:
            ms_g += f"\n<b>Score</b> - <code>{score}</code>"
        ms_g += "\n<b>Genres</b> - "
        for x in json.get("genres", []):
            ms_g += f"{x}, "
        ms_g = ms_g[:-2]

        image = json.get("bannerImage", False)
        ms_g += (
            (f"\n<i>{json.get('description', None)}</i>")
            .replace("<br>", "")
            .replace("</br>", "")
        )
        if image:
            try:
                await message.reply_photo(image, caption=ms_g)
            except:
                ms_g += f" [〽️]({image})"
                await message.reply(ms_g)
        else:
            await message.reply(ms_g)


@register(cmds="upcoming")
@disableable_dec("upcoming")
async def upcoming(message):
    jikan = jikanpy.jikan.Jikan()
    upcoming = jikan.top("anime", page=1, subtype="upcoming")

    upcoming_list = [entry["title"] for entry in upcoming["top"]]
    upcoming_message = ""

    for entry_num in range(len(upcoming_list)):
        if entry_num == 10:
            break
        upcoming_message += f"{entry_num + 1}. {upcoming_list[entry_num]}\n"

    await message.reply(upcoming_message)


async def site_search(message, site: str):
    args = message.text.split(" ", 1)
    more_results = True

    try:
        search_query = args[1]
    except IndexError:
        await message.reply("Give something to search")
        return

    if site == "kaizoku":
        search_url = f"https://animekaizoku.com/?s={search_query}"
        html_text = requests.get(search_url).text
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        search_result = soup.find_all("h2", {"class": "post-title"})

        if search_result:
            result = f"<b>Search results for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>AnimeKaizoku</code>: \n"
            for entry in search_result:
                post_link = entry.a["href"]
                post_name = html.escape(entry.text)
                result += f"• <a href='{post_link}'>{post_name}</a>\n"
        else:
            more_results = False
            result = f"<b>No result found for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>AnimeKaizoku</code>"

    elif site == "kayo":
        search_url = f"https://animekayo.com/?s={search_query}"
        html_text = requests.get(search_url).text
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        search_result = soup.find_all("h2", {"class": "title"})

        result = f"<b>Search results for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>AnimeKayo</code>: \n"
        for entry in search_result:

            if entry.text.strip() == "Nothing Found":
                result = f"<b>No result found for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>AnimeKayo</code>"
                more_results = False
                break

            post_link = entry.a["href"]
            post_name = html.escape(entry.text.strip())
            result += f"• <a href='{post_link}'>{post_name}</a>\n"

    elif site == "ganime":
        search_url = f"https://gogoanime.so//search.html?keyword={search_query}"
        html_text = requests.get(search_url).text
        soup = bs4.BeautifulSoup(html_text, "html.parser")
        search_result = soup.find_all("h2", {"class": "title"})

        result = f"<b>Search results for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>gogoanime</code>: \n"
        for entry in search_result:

            if entry.text.strip() == "Nothing Found":
                result = f"<b>No result found for</b> <code>{html.escape(search_query)}</code> <b>on</b> <code>gogoanime</code>"
                more_results = False
                break

            post_link = entry.a["href"]
            post_name = html.escape(entry.text.strip())
            result += f"• <a href='{post_link}'>{post_name}</a>\n"

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="See all results", url=search_url)
    )

    if more_results:
        await message.reply(result, reply_markup=buttons, disable_web_page_preview=True)
    else:
        await message.reply(result)


@register(cmds="kaizoku")
@disableable_dec("kaizoku")
async def kaizoku(message):
    await site_search(message, "kaizoku")


@register(cmds="kayo")
@disableable_dec("kayo")
async def kayo(message):
    await site_search(message, "kayo")


@register(cmds="ganime")
@disableable_dec("ganime")
async def kayo(message):
    await site_search(message, "ganime")


@anime.on_message(filters.command("aq"))
def quote(_, message):
    quote = requests.get("https://animechan.vercel.app/api/random").json()
    message.reply_text('`'+quote['quote']+'`\n '+quote['anime']+' (In '+quote['character']+')')


# added ganime search based on gogoanime.so

STICKERS = (
    "CAACAgUAAxkBAAECbnZgyJGEHyCnDatqd4JGXjHY70WvEQACTwMAAjQsSVYUEq35xsptRh8E",
    "CAACAgUAAxkBAAECbnRgyJGBCL0pg7RixVWueHiPjHiRRgAC_wIAAgnlSFZJPIervh8EIR8E",
    "CAACAgUAAxkBAAECbnJgyJF-YqDEPhtmodbo08527gdIygACwAIAAvmCQVZ-bxgbwQ5NAR8E",
    "CAACAgUAAxkBAAECbnBgyJF7sPfpwPOxYF1l67pS4ErMoQACdAIAAt8gQFZ3Lz2I-QPBqR8E",
    "CAACAgUAAxkBAAECbm5gyJF4pGEKnaHAOC8dVPndlEU_CAACYgMAAswnSFbISeAgaEn-bR8E",
    "CAACAgUAAxkBAAECbmxgyJF1g20MLWEjoDc1JTa-D2nYbwAC6QIAAij-QVYvfd0ZM75hsx8E",
    "CAACAgUAAxkBAAECbmpgyJFy5zPnw5lJtoJsZMSZvBplHwACuQMAAuIGSFYw81FumLX8Eh8E",
    "CAACAgUAAxkBAAECbmhgyJFuotCmFcfxdlDdFZIGgBteUgAC4gMAAsQiQFYUOe36d0r-AR8E",
    "CAACAgUAAxkBAAECbmZgyJFqqBgttWfU_3TACAYYi3jyLQACcQIAAk5hSFZygDWfQcCZLx8E",
    "CAACAgUAAxkBAAECbmRgyJFn5ebhMv7UWW6GTeIVVf5khwACtAIAAhJGQFY0gAIrBE30_R8E",
    "CAACAgUAAxkBAAECbmJgyJFjfag_Zr8hj1RRPNx1omF3YgACgQUAAqkfQVZuMEm8vuyrGh8E",
    "CAACAgUAAxkBAAECbmBgyJFfW5l_1xki6Hpvi_GMDiWljgACjAMAApbASFapmnDbRe377h8E",
    "CAACAgUAAxkBAAECbl5gyJFciybp2Cd6_MStR2kIf98wwgACQwUAApU3QFa5fVWzsOwf-R8E",
    "CAACAgUAAxkBAAECblxgyJFZ4CwK0IJ0au84hl5YO6l3EQAC_AIAAoo_SVaPIWegOBH9oB8E",
    "CAACAgUAAxkBAAECblpgyJFW-QABvvE0348fRLQ8gjhwOpgAAtQCAAKfP0BWRg9iH8kvztkfBA",
    "CAACAgUAAxkBAAECblhgyJFTe82K9IcJ-5NgoDEG-oAiegACKgMAAovVQVblVv56L9t4_B8E",
    "CAACAgUAAxkBAAECblZgyJFQPHTr9OtJ_p-l0dMWpji9-QACewMAAjO9QFa4vqP5TvZUSh8E",
    "CAACAgUAAxkBAAECblRgyJFMAWr0YXY8_NhJuZZqzVNyzQACDAMAAkywSFaGyfJxA2ZtCx8E",
)


@register(cmds="alola")
async def alola(message):
    await message.reply_sticker(random.choice(STICKERS))


__mod_name__ = "🔮Anime"

__help__ = """
Get information about anime, manga or anime characters.

<b>Available commands:</b>
- /anime (anime): returns information about the anime.
- /character (character): returns information about the character.
- /manga (manga): returns information about the manga.
- /airing (anime): returns anime airing info.
- /kaizoku (anime): search an anime on animekaizoku.com
- /kayo (anime): search an anime on animekayo.com
- /ganime (anime): search an anime on gogoanime.so
- /upcoming: returns a list of new anime in the upcoming seasons.
- /aq : get anime random quote
- /alola : Get Alola characters stickers
"""
