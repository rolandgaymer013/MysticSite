from typing import List
from core.models import Item, Crate, MiscellaneousGroup, MiscellaneousItem
from sqlalchemy import desc
from atn import server_custom_tags
def errorMaker(errorCode: int | str = "???") -> List[Item]:
    resp = Item
    resp.ItemHTML = f"""
        <div><span style="color: #FF6CE9; ">☆ </span><span style="color: #CE9DDA; ">O</span><span style="color: #B6B6D3; ">o</span><span style="color: #9DCECC; ">p</span><span style="color: #85E7C4; ">s</span><span style="color: #6CFFBD; ">i</span><span style="color: #89E2C6; ">e</span><span style="color: #A7C4CF; ">s</span><span style="color: #C4A7D7; ">! </span><span style="color: #FF6CE9; ">☆</span></div>
        <div><span style="color: #55FF55; ">Sadness 420</span></div>
        <div><span style="color: #55FF55; ">Hope 69</span></div>
        <div><span style="color: #55FF55; ">Error Code {errorCode}</span></div>
        <div><span style="color: #AAAAAA; ">- - - - - ▶ </span><span style="color: #E289E0; ">E</span><span style="color: #D398DC; ">r</span><span style="color: #C4A7D7; ">r</span><span style="color: #B6B6D3; ">o</span><span style="color: #A7C4CF; ">r </span><span style="color: #89E2C6; ">C</span><span style="color: #7BF0C1; ">o</span><span style="color: #6CFFBD; ">l</span><span style="color: #7CEFC2; ">l</span><span style="color: #8DDEC7; ">e</span><span style="color: #9DCECC; ">c</span><span style="color: #ADBED1; ">t</span><span style="color: #BEADD5; ">i</span><span style="color: #CE9DDA; ">o</span><span style="color: #DE8DDF; ">n </span><span style="color: #AAAAAA; ">◀ - - - - -</span></div>
        <div><br></div>
        <div><span style="color: #FFFF55; ">Error, no results found :(</span></div>
        <div><span style="color: #FFFF55; ">If you believe the site is broken,</span></div>
        <div><span style="color: #FFFF55; ">please contact AlexTheNerd on discord!</span></div>
        <div><br></div>
        <div><span style="color: #AAAAAA; ">- - - - - - - - - - - - - - - - - - - - - -</span></div>
        <div><span style="color: #AAAAAA; ">Rarity: </span><span style="color: #55FF55; ">Common :(</span></div>"""
        
    return([resp]) # type: ignore


def currentCrateData():
    crates = Crate.query.order_by(desc(Crate.id))
    formattedCrates = {}
    for crate in crates.all():
        formattedCrates[crate.id] = {
            "CrateName" : crate.CrateName,
            "ReleaseDate" : crate.ReleaseDate,
            "URLTag" : crate.URLTag,
            "CrateType" : crate.CrateType
        }
    if formattedCrates:
        return formattedCrates
    return None

def currentGroupData():
    groups = MiscellaneousGroup.query.order_by(desc(MiscellaneousGroup.id))
    formattedGroups = {}
    for group in groups.all():
        formattedGroups[group.id] = {
            "GroupName" : group.GroupName,
            "ReleaseDate" : group.ReleaseDate,
            "URLTag" : group.URLTag,
            "GroupType" : group.GroupType,
            "Notes" : group.Notes
            
        }
    if formattedGroups:
        return formattedGroups
    return None

PrettyRoutes = {
    "/" : "Home",
    "/all" : "All Items",
    "/stats" : "Item Statistics",
    "/itemtracker" : "Item Tracker",
    "/infinitetracker" : "Infinite Tracker",
    "/armortracker" : "Armor Tracker",
    "/tooltracker" : "Tool Tracker",
    "/weapontracker" : "Weapon Tracker",
    "/jobspayouts" : "Jobs Payouts",
    "/gamble" : "Gamble",
    "/tags" : "Tag List",
    "/crates" : "Crate List",
    "/blockspeed" : "Block Speed Calc.",
    "/tag/Armor/all" : "Armor",
    "/tag/Tools/all" : "Tools",
    "/tag/Weapons/all" : "Weapons",
    "/login" : "Login",
    "/search" : "Advanced Search",
    "/inventory" : "Inventory Planner"
}

tags = {
    "Armor" : [
        "Hat",
        "Helmet",
        "Chestplate",
        "Leggings",
        "Boots",
        "Elytra"
    ],
    "Tools" : [
        "Pickaxe",
        "Axe",
        "Hoe",
        "Shovel",
        "Rod",
        "Shield",
        "Shears"
    ],
    "Weapons" : [
        "Crossbow",
        "Sword",
        "Axe",
        "Bow",
        "Trident",
        "Mace"
    ]
}
nonCatTags: List[str] = [
    "Infinite",
    "Offhand",
    "Hotbar",
    "Inventory",
    "Special Block",
    "Quest",
    "Disguise",
    "Repeat Appearance",
    "Unbreakable Kit",
    "Head Dropping",
    "Egg Dropping",
    "Mob Capturing",
    "Cooker",
    "Teleportation",
    "Quest Only",
    "Treefeller",
    "Veinminer",
    "Axe Projectile",
    "Radius Breaking",
    "Block Counter",
    "Bleed",
    "Kill Counter",
    "Telekinesis",
    "Speed Attribute",
    "Custom Loot",
    "Furniture Dropping",
    "Auto Replant",
    "Reach Distance"
]
if server_custom_tags:
    nonCatTags += server_custom_tags
validTags = []
for category, tagList in tags.items():
    for tag in tagList:
        route = f"/tag/{category}/{tag}"
        pretty = f"{tag}"
        PrettyRoutes[route] = tag
        if tag not in validTags:
            validTags.append(tag)
for tag in nonCatTags:
    route = f"/tag/Misc/{tag}"
    pretty = f"{tag}"
    PrettyRoutes[route] = tag
    if tag not in validTags:
        validTags.append(tag)



for category, tagList in tags.items():
    for tag in tagList:
        route = f"/tag/{category}/{tag}"
        pretty = f"{tag}"
        PrettyRoutes[route] = tag

validSetTypes = [
    "Armor Set",
    "Upgrade"
]

validMiscGroupTypes = [
    "Voucher",
    "Event",
    "Furniture",
    "Crate Based Vouchers"
]


blocksForBreakSpeedCalculator = {
    "Pickaxe" : {
        "Netherrack/Nylium" : 0.4,
        "Ice/Packed Ice" : 0.5,
        "Block of Quartz" : 0.8,
        "Sandstone/Red Sandstone" : 0.8,
        "Terracotta" : 1.25,
        "Basalt" : 1.25,
        "Glazed Terracotta" : 1.4,
        "Stone/Diorite/Andesite/Granite/Tuff" : 1.5,
        "Concrete" : 1.8,
        "Cobblestone" : 2.0,
        "Blue Ice" : 2.8,
        "Gold/Lapis/Copper Blocks" : 3.0,
        "Coal/Copper/Diamond/Emerald/Gold/Iron/Lapis/Redstone Ore Blocks" : 3,
        "Endstone" : 3,
        "Nether Quartz/Nether Gold Ore Blocks" : 3.0,
        "Blast Furnace" : 3.5,
        "Cobbled Deepslate" : 3.5,
        "Deepslate Coal/Copper/Diamond/Emerald/Gold/Iron/Lapis/Redstone Ore Blocks" : 4.5,
        "Coal/Diamond/Emerald/Iron/Redstone Blocks" : 5.0,
        "Raw Gold/Raw Copper/Raw Iron Blocks" : 5.0,
        "Ender Chest" : 22.5,
        "Ancient Debris" : 30.0,
        "Obsidian/Crying Obsidian/Block of Netherite" : 50.0
    },
    "Axe" : {
        "Mushroom Block" : 0.2,
        "Bee Nest" : 0.3,
        "Mangrove Roots" : 0.7,
        "Bamboo/Pumpkin/Melon" : 1.0,
        "Logs/Planks" : 2.0,
        "Chest" : 2.5
    },
    "Hoe" : {
        "Moss Blocks" : 0.1,
        "Leaves/Sculk" : 0.2,
        "Hay Bale" : 0.5,
        "Sponge" : 0.6,
        "Nether/Warped Wart Block/Shroomlight" : 1.0,
        "Sculk Sensor" : 1.5,
        "Sculk Catalyst/Sculk Shrieker" : 3.0
    },
    "Shovel" : {
        "Snow Block" : 0.2,
        "Coarse Dirt/Dirt/Mud/Podzol" : 0.5,
        "Concrete Powder" : 0.5,
        "Sand/Red Sand" : 0.5,
        "Soul Sand/Soul Soil" : 0.5,
        "Clay/Farmland/Grass Block/Gravel/Mycelium" : 0.6 
    },
    "Shears" : {
        "Leaves/Vines" : 0.2,
        "Wool" : 0.8,
        "Cobweb" : 4.0
    }
}


Changelog = {
    "2/19/2025" : [
        ("mc-gold", "Corrected spelling mistake on Stats page."),
        ("mc-gold", "Setup auto deployment from dev environment.")
    ],
    "2/21/2025" : [
        ("mc-gold", "Added Item Tracker! Thank you SaltyAssassin for the suggestion!")
    ],
    "2/22/2025" : [
        ("mc-gold", "Moved the page showing all items to a secondary page, in an effort to help people with less than stellar internet connections still use the site. Thank you KaylaKrow for the suggestion!"),
        ("mc-gold", "Moved changelog to the main page.")
    ],
    "3/2/2025" : [
        ("mc-gold", "Reworked Navbar to bring me more joy."),
        ("mc-gold", "Added Infinite specific item tracker."),
        ("mc-gold", "Reworked database and created a database builder to make it easier to modify items.")
        
    ],
    "3/9/2025" : [
        ("mc-gold", "Item/Infinite trackers now persistently store your items! Thank you Katie for the suggestion!")
    ],
    "3/16/2025" : [
        ("mc-gold", "Corrected a database error leading to no swords being listed under <a href=\"/tag/Weapons/Sword\">Swords</a>, thank you LostWoodsOne for bringing this to my attention!")
    ],
    "6/3/2025" : [
        ("mc-gold", "Added <a href=\"/gamble\">Gambling</a>! Thank you BR_MarkoTheGamer for the suggestion!"),
        ("mc-gold", "Removed some redundant HTML tags (why were there 47 extra &lt;/li&gt; tags in the navbar??)"),
        ("mc-gold", "Added a Page View Tracker (again)")
    ],
    "6/5/2025" : [
        ("mc-green", "<a href=\"/gamble\">Gambling</a> is now weighted as it is in-game!"),
        ("mc-light-purple", "Cleaned up the Gambling Menu."),
        ("mc-green", "Added overviews to the gambling menu, so you can see what you got at a glance instead of looking through individually."),
        ("mc-light-purple", "Added a limit to how many rolls you could do at once. (turns out things get a bit wild when you try and roll 1,000,000 items :p)"),
        ("mc-red", "Corrected a bug where the changelog would break if you didn't also search for an item."),
        ("mc-red", "Pickaxes that appear in multiple crates now appear on their crate pages, they can also be pulled during gambling.")
    ],
    "6/11/2025" : [
        ("mc-gold", "Adjusted CSS (stupid fucking bootstrap) to be a bit more consistent and readable across the site."),
        ("mc-green", f"Made it so crate summaries for <a href=\"/gamble\">Gambling</a> show the colored item names."),
        ("mc-green", "Removed the silly gap space between tiles. (I'm still unsure if I like this better or not, may be reverted :s)")
    ],
    "6/14/2025" : [
        ("mc-gold", "Cleaned up some more HTML code."),
        ("mc-gold", "Standardized the code for displaying items into one file, to be shared across the site.")
    ],
    "7/7/2025" : [
        ("mc-green", "New tagging system, all items can now have up to 2 'keywords' (Offhand, Helmet) for better organization. This should help to narrow down searches a bit more."),
        ("mc-green", "Added item type to all items(minecraft:bow), should improve readability of site."),
        ("mc-green", "Slightly more automated changelog."),
        ("mc-green", "More navbar shenanigans!"),
        ("mc-gold", "Fully rewrote backend to support adding new items directly to the site. I was fully rebuilding the database previously with the old system."),
    ],
    "7/12/2025" : [
        ("mc-green", "Items can now support Tertiary Tags"),
        ("mc-light-purple", "Gambling item limit 10,000 -> 1,000.")
    ],
    "7/19/2025" : [
        ("mc-green", "Added randomized background colors!"),
        ("mc-light-purple", "Navbar swapped over to dark mode."),
        ("mc-green", "Changelogs now use different colors to denote different types of updates, 5 free keys to the first person who correctly guesses my intent for each currently used color. (6/14 and earlier are not updated colors wise.)"),
        ("mc-light-purple", "Buffed out some corners around the site, tables are hopefully a little less jarring to look at.")
    ],
    "7/26/2025" : [
        ("mc-green", "Adjusted page titles to prettier names for each public page.")
    ],
    "8/3/2025" : [
        ("mc-gold", "Whole new addition on the backend. I can now adjust the order that items appear in if I need to make adjustments later on."),
        ("mc-red", "Disabled the Masonry tiling, decided I don't love it."),
        ("mc-gold", "Backend Dashboard is now setup to supply the Discord Bot with a different item name as needed (prom level 2 and whatnot)"),
        ("mc-green", "Clicking an item on the bot or on the website will now take you to a screen showing far more detailed item information. Including tags or other notes that I've added (currently only 2 items have notes, see if you can find them)")
    ],
    "8/6/2025" : [
        ("mc-green", "Both Infinite tracker and Item tracker now generate a Discord formatted list, to make your shopping lists that much easier!")
    ],
    "8/18/2025" : [
        ("mc-green", "<a href=\"/search\">Advanced Search</a> is now available!")
    ],
    "8/19/2025" : [
        ("mc-light-purple", "Background colors normalized, should shave off some ms during load time."),
        ("mc-light-purple", "Spacing between columns adjusted, reduces amount of html tags loaded per page as well by a wide margin. Should also reduce load time.")
    ],
    "9/17/2025" : [
        ("mc-green", "Site now supports Quantary and Quinary tags.")
    ],
    "10/16/2025" : [
        ("mc-green", "<a href=\"/armortracker\">Armor Tracker</a> now live!"),
        ("mc-light-purple", "Optimized the way the various trackers load items in. I was stupid before and it would do a new database request for every crate. It now does 1 request for all items, and 1 request for all crates, then sorts it out from there.")
    ],
    "10/26/2025" : [
        ("mc-green", "Added a new block break speed calculator! Ever wondered which tools might instamine a certain block? Now you can check that <a href=\"/blockspeed\">here</a>!")
    ],
    "12/7/2025" : [
        ("mc-light-purple", "Item trackers will now load much faster. I made a rather severe mistake, leading to the site attempting to rebuild the missing items list once for every item on screen, every single checkbox you press."),
        ("mc-green", "Item Trackers now have 'Check All' and 'Uncheck All' buttons! Perfect for those of you who already have borderline everything!")
    ],
    "1/7/2026" : [
        ("mc-green", "Crate list is now it's own page. Sorted by both type and release date."),
        ("mc-green", "Tag list is now it's own page. Sorted by type."),
        ("mc-green", "New tags added! <code>Treefeller, Veinminer, Axe Projectile, Radius Breaking, Block Counter, Bleed, Reach Distance, Kill Counter, Auto Replant, Telekinesis, Speed Attribute, Custom Loot, and Furniture Dropping</code>"),
        ("mc-green", "Full item list is now paginated, this should help for those of you with shitty internet."),
        ("mc-light-purple", "Admin users now go straight to manage item screen when clicking an item preview."),
        ("mc-light-purple", "Advanced search now supports up to 3 tags in the same search."),
        ("mc-light-purple", "Add tag usage counts onto the tag page.")
    ],
    "2/23/2026" : [
        ("mc-green", "Inventory planner is now a thing! Use this tool to build a loadout and share it with others! <a href=\"/inventory\">Here it is!</a>")
    ],
    "3/10/2026" : [
        ("mc-light-purple", "When an invalid item ID is used on <code>/item</code>, the site no longer tells you to fuck off."),
        ("mc-light-purple", "Search bar now automatically handles Roman Numeral/Integer conversions. Meaning <code>Efficiency 10</code> and <code>Efficiency X</code> will return the same results."),
        ("mc-light-purple", "Advanced search now automatically handles Roman Numeral/Integer conversions. Meaning <code>Efficiency 10</code> and <code>Efficiency X</code> will return the same results."),
        ("mc-light-purple", "Advanced search now supports & for the search term. Meaning you could do a search term such as: <code>set & haste 4</code> to find all items with both haste 4, and the word set (usually means a set bonus).")
    ],
    "3/11/2026" : [
        ("mc-light-purple", "The Item Tracker has been updated to use a new export format, the old one would show incorrect data if an item was ever deleted from the database."),
        ("mc-light-purple", "The Item Tracker now has the option to Upload Data, this is used for bot developers who are interested in doing something with people's inventory data, such as a bot that calculates your networth."),
        ("mc-light-purple", "The Item Tracker is now condensed to have all the items on the same page, you can filter through each one with the Tag Selection tile."),
        ("mc-green", "New sets feature has been added! This will show related items together on the same screen, such as items needed for an upgrade, or Armor Sets! Please note, it will take a while for some servers to see this actively used, and some items can/will get missed.")
    ],
    "3/12/2026" : [
        ("mc-light-purple", "Fixed <code>/gambling</code>"),
        ("mc-light-purple", "Fixed <code>/blockspeed</code>"),
        ("mc-green", "New sets feature added! This is intended for Armor Sets with a bonus, or for item required for an Upgrade Quest"),
        ("mc-gold", "Debug mode discovered and enabled in dev environment.")
    ],
    "3/15/2026" : [
        ("mc-gold", "Item description images used by the bot are now generated automatically once an hour, if needed."),
        ("mc-light-purple", "Instructions and explanations have been added to nearly every page on the site."),
        ("mc-gold", "Item Icon images can now be uploaded directly to the website, rather than git commits being used.")
    ],
    "3/20/2026" : [
        ("mc-gold", "Login system has been updated to actually have minimum safety requirements."),
        ("mc-gold", "Permission system has been implemented, so different people can have different levels of access to the site."),
        ("mc-gold", "Admin actions are now logged in the database. This is incase someone decides to be a piece of shit and grief the site.")
    ],
    "3/21/2026" : [
        ("mc-light-purple", "Items on the item tracker are now sorted by the custom Item Order I've setup.")
    ],
    "3/27/2026" : [
        ("mc-light-purple", "Search bar and <code>/search</code> now search item notes as well."),
        ("mc-light-purple", "Search bar now supports <code>&</code> in searches.")
    ],
    "3/28/2026" : [
        ("mc-gold", "<code>/admin/uploadIcon</code> now shows item preview to make things easier.")
    ],
    "3/29/2026" : [
        ("mc-gold", "<code>/admin/setMaker</code> now shows item names when making a set instead of item ids."),
        ("mc-gold", "<code>/admin/manageItem</code> now shows item icons."),
    ],
    "4/3/2026" : [
        ("mc-green", "Miscellaneous item support is now added! This will primarily be used for Voucher items such as plushies, event items/rewards, and possibly furniture in the future."),
    ],
    "4/4/2026" : [
        ("mc-gold", "Icon images implemented into <code>/admin/manageItem</code> for both miscellaneous items and for crate items."),
        ("mc-gold", "Item lists now show current icon when hovering.")
    ],
    "4/5/2026" : [
        ("mc-gold", "Users now have the ability to reset their passwords when logged in."),
        ("mc-gold", "Site admins can now force a password reset if a user cannot log in for some reason or another."),
    ],
    "7/31/2026" : [
        ("mc-gold", "Item Tracker now shows the colorful names of items, when no duplicates exist with that same name."),
        ("mc-gold", "Item Tracker now shows the number of items collected out of how many exist."),
    ]
    
}

        
Changelog = dict(reversed(list(Changelog.items())))