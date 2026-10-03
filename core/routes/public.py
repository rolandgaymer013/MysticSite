from flask import render_template, request, flash, url_for, redirect
from sqlalchemy import or_, and_, not_

from core import app, db
from core import config as c

from core.models.sets import Set as ItemSets
from core.models import Item, Crate, ItemTracker, MiscellaneousGroup, MiscellaneousItem
from core.utils import convert_int_to_roman, convert_roman_in_string, randomCode

from atn import server_rarity_list, server_name
try:
    from atn import jobsInfo, JobsSecrets
except:
    jobsInfo = None
    JobsSecrets = None
from random import choices
from sys import platform
from typing import List


import json
from collections import Counter

TagCols = [Item.TagPrimary, Item.TagSecondary, Item.TagTertiary, Item.TagQuaternary, Item.TagQuinary, Item.TagSenary, Item.TagSeptenary]
def noDupes(items: list[Item]) -> list[Item]:
    returnItems = [item for item in items if "Repeat Appearance" not in [item.TagPrimary, item.TagSecondary, item.TagTertiary, item.TagQuaternary, item.TagQuinary, item.TagSenary, item.TagSeptenary]]
    return returnItems

def SingleTagQuery(tag: str) -> list[Item]:
    return Item.query.filter(or_(col.is_(tag) for col in TagCols)).order_by(Item.ItemOrder).all() # type: ignore

def getAlternateNumbers(input: str) -> List[str]:
    return [input, convert_int_to_roman(input), convert_roman_in_string(input)]

def getTermFilters(term: str, itemType: Item | MiscellaneousItem):
    terms = term.split("&")
    conditions = []
    for user_term in terms:
        user_term = user_term.strip()
    
        filters = or_(*[itemType.ItemHuman.contains(term) for term in getAlternateNumbers(user_term)])
        filters += or_(*[itemType.Notes.contains(term) for term in getAlternateNumbers(user_term)])
        conditions.append(filters)
    return conditions

@app.route('/', methods=('GET', 'POST'))
def index():
    items = None
    if request.method == 'POST':
        search = request.form['search']
        if not search: 
            flash("Try entering a query!")
        conditions = []
        
        conditions += getTermFilters(search, Item) # type: ignore
            
        items = Item.query.where(*conditions).order_by(Item.ItemOrder).all()
        if not items:
            items = None
            flash("No results found!")
    if items:
        items = noDupes(items)     
    return render_template("public/index.html", Items = items)

@app.route('/changelog')
def changelog(): 
    return render_template("public/changelog.html", ChangeLog = c.Changelog)

@app.route('/search', methods = ['GET', 'POST']) # type: ignore
def search():
    formattedCrates = c.currentCrateData()
    rarityList = server_rarity_list
    items = []
    miscItems = []
    recentTerm, recentCrate, recentTag, recentTagTwo, recentTagThree, recentRarity = ("", "", "", "", "", "")
    if request.method == 'POST':
        form = request.form.to_dict()
        conditions = []
        miscConditions = []
        if form["Term"]:
            recentTerm = form["Term"]
            
            conditions += getTermFilters(recentTerm, Item)
            miscConditions += getTermFilters(recentTerm, MiscellaneousItem)
            #conditions.append(Item.ItemHuman.ilike(f'%{form["Term"]}%'))
        if form["Crate"]:
            recentCrate = form["Crate"]
            conditions.append(Item.CrateID == int(form["Crate"]))
        if form["Tag"]:
            recentTag = form["Tag"]
            conditions.append(or_(col.is_(form["Tag"]) for col in TagCols)) # type: ignore
        if form["TagTwo"]:
            recentTagTwo = form["TagTwo"]
            conditions.append(or_(col.is_(form["TagTwo"]) for col in TagCols)) # type: ignore
        if form["TagThree"]:
            recentTagThree = form["TagThree"]
            conditions.append(or_(col.is_(form["TagThree"]) for col in TagCols)) # type: ignore
        if form["Rarity"]:
            recentRarity = form["Rarity"]
            rarity = ""
            if form["Rarity"] in rarityList:
                rarity = form["Rarity"]
                conditions.append(Item.RarityHuman.ilike(f"%{rarity}%"))
            if form["Rarity"] == "0":
                conditions.append(Item.RarityHuman.is_(""))

            
            
            
        items: List[Item] = Item.query.where(*conditions).order_by(Item.ItemOrder).all()
        
        inputs = [
            recentCrate,
            recentTag,
            recentTagTwo,
            recentTagThree,
            recentRarity
        ]
        doMisc = True
        for inp in inputs:
            if inp != "":
                doMisc = False
                break
        if recentTerm and doMisc:
            miscItems: List[MiscellaneousItem] = MiscellaneousItem.query.where(*miscConditions).order_by(MiscellaneousItem.ItemOrder).all()
        if len(items) == 0 and len(miscItems) == 0:
            flash("No Results Found!", "dark")
    return render_template("public/search.html",
                           validTags = c.validTags,
                           currentCrates = formattedCrates,
                           rarityList = rarityList,
                           Items = items,
                           MiscItems = miscItems,
                           recentTerm = recentTerm,
                           recentTag = recentTag,
                           recentTagTwo = recentTagTwo,
                           recentTagThree = recentTagThree,
                           recentCrate = recentCrate,
                           recentRarity = recentRarity)

@app.route('/all')
@app.route('/all/<int:page>/')
@app.route('/all/<int:page>/<int:quantity>')
def all(page: int=1, quantity:int=25):
    pagination = Item.query.order_by(Item.ItemOrder).paginate(page=page, per_page=quantity, error_out=False)
    return render_template("public/allitems.html", Items = pagination.items, pagination = pagination)
        

@app.route('/item/<itemID>')
def item(itemID):
    item: Item | None = Item.query.filter_by(id = itemID).one_or_none()
    if item:
        PrimaryCrate: Crate = Crate.query.filter_by(id = item.CrateID).first() # type: ignore
        PrimaryConnectedGroup = MiscellaneousGroup.query.filter_by(id = item.ConnectedItems).one_or_none()
        item.CrateName = PrimaryCrate.CrateName
    else:
        item = Item()
        item.ItemHTML = "<div class='mc-gold'>This is not a valid item id. Try again, or don't, it's not actually my problem.</div>"
        item.id = 0
        PrimaryCrate = None # type: ignore
        PrimaryConnectedGroup = None
    return render_template("public/singleItem.html", PrimaryItem = item, PrimaryGroup = PrimaryConnectedGroup)

@app.route('/rawitem/<itemID>')
def rawitem(itemID):
    try:
        item = Item.query.filter_by(id = itemID).first() # type: ignore
    except:
        item = [c.errorMaker(404)]
    return render_template("public/raw.html", item = item)

@app.route('/rawmiscitem/<itemID>')
def rawMiscitem(itemID):
    try:
        item = MiscellaneousItem.query.filter_by(id = itemID).first() # type: ignore
    except:
        item = [c.errorMaker(404)]
    return render_template("public/raw.html", item = item)

@app.route('/crate/<crateTag>')
def crate(crateTag):
    try:
        crateID = Crate.query.filter_by(URLTag = crateTag).first().id # type: ignore
        items = Item.query.filter_by(CrateID = crateID).order_by(Item.ItemOrder) # type: ignore
    except:
        items = [c.errorMaker(404)]
    return render_template("public/mainDisplay.html", Items = items)

@app.route('/crates')
def cratePage():
    crates: List[Crate] = Crate.query.all()
    crateList = {
        "Seasonal" : [],
        "Side" : [],
        "Misc" : [],
        "" : []
        }
    for crate in crates:
        for key in crateList.keys():
            if crate.CrateType == key:
                crateList[key].append(crate)
    for key in list(crateList.keys()):
        if len(crateList[key]) == 0:
            del crateList[key]
    return render_template("public/crate.html", SortedCrates = crateList)


@app.route('/group/<groupTag>')
def group(groupTag):
    try:
        group = MiscellaneousGroup.query.filter_by(URLTag = groupTag).first()
        if not group:
            flash("Group not found.")
            return redirect('/groups')
        parentItems = Item.query.filter_by(ConnectedItems = group.id).all()
        items = MiscellaneousItem.query.filter_by(GroupID = group.id).order_by(MiscellaneousItem.ItemOrder)
        if not items:
            flash("No items found in group.")
            return redirect('/groups')
    except:
        flash("Something went wrong.")
        return redirect('/groups')

    return render_template("public/mainDisplay.html", Items = items, Group = group, alternativeDisplay = True, ParentItems = parentItems)

@app.route('/groups')
def groupPage():
    groups: List[MiscellaneousGroup] = MiscellaneousGroup.query.order_by(MiscellaneousGroup.GroupOrder).all()
    
    grouped_data = {}
    
    for groupType in c.validMiscGroupTypes:
        grouped_data[groupType] = {}
    grouped_data["Unsorted"] = {}

    for group in groups:
        g_type = group.GroupType if group.GroupType in grouped_data else "Unsorted"
        
        if " - " in group.GroupName:
            parts = group.GroupName.split(" - ", 1)
            series_name = parts[0].strip()
            sub_category = parts[1].strip()
        else:
            series_name = group.GroupName.strip()
            sub_category = "Full Set"

        if series_name not in grouped_data[g_type]:
            grouped_data[g_type][series_name] = {
                "release_date": group.ReleaseDate or "",
                "sub_items": []
            }
        
        grouped_data[g_type][series_name]["sub_items"].append({
            "sub_category": sub_category,
            "url_tag": group.URLTag,
            "full_name": group.GroupName,
            "release_date": group.ReleaseDate or ""
        })

    cleaned_data = {k: v for k, v in grouped_data.items() if len(v) > 0}

    return render_template("public/groups.html", Hierarchy=cleaned_data)


@app.route('/tags')
def tagsPage():
    stats = Counter()

    rows = Item.query.with_entities(
        Item.TagPrimary,
        Item.TagSecondary,
        Item.TagTertiary,
        Item.TagQuaternary,
        Item.TagQuinary,
        Item.TagSenary,
        Item.TagSeptenary,
    ).all()

    for row in rows:
        for tag in row:
            if tag:
                stats[tag] += 1
    return render_template("public/tags.html", stats=stats, tags = c.server_custom_tags)

@app.route('/tag/<cat>/<tag>')
def tag(cat, tag):
    items = None
    if cat in c.tags:
        if tag == "all":
            items = Item.query.filter(
                or_(
                    or_(Item.TagPrimary == x for x in c.tags[cat]), # type: ignore
                    or_(Item.TagSecondary == x for x in c.tags[cat]), # type: ignore
                    or_(Item.TagTertiary == x for x in c.tags[cat]), # type: ignore
                    or_(Item.TagQuaternary == x for x in c.tags[cat]), # type: ignore
                    or_(Item.TagQuinary == x for x in c.tags[cat]), #type: ignore
                    or_(Item.TagSenary == x for x in c.tags[cat]), #type: ignore
                    or_(Item.TagSeptenary == x for x in c.tags[cat]) #type: ignore
                )
            ).order_by(Item.ItemOrder).all()
        else:
            items = SingleTagQuery(tag) # type: ignore
    if cat == 'Misc':
        items = SingleTagQuery(tag) # type: ignore
    return render_template("public/mainDisplay.html", Items = noDupes(items) if tag != "Repeat Appearance" else items) # type: ignore


@app.route('/stats')
def stats():
    stats = Counter()

    rows = Item.query.with_entities(
        Item.TagPrimary,
        Item.TagSecondary,
        Item.TagTertiary,
        Item.TagQuaternary,
        Item.TagQuinary,
        Item.TagSenary,
        Item.TagSeptenary,
    ).all()

    for row in rows:
        for tag in row:
            if tag:
                stats[tag] += 1
    #for tag in c.validTags:
    #    stats[tag] = query.filter(or_(col.is_(tag) for col in TagCols)).count() #type: ignore
    stats["Crate"] = Crate.query.count()
    return render_template("public/stats.html", stats = stats, total=Item.query.count())



@app.route('/itemtracker', methods=('GET', 'POST'))
def newitemtracker():
    if request.method == 'POST':
        code = json.loads(request.form['importCode'])
        if len(code) < 1:
            flash("Code must have at least one item to upload.")
        else:
            attemptedSearch = ItemTracker.query.filter(ItemTracker.ItemList == str(code)).first()
            if attemptedSearch:
                flash(f"Your upload code is: <code>{attemptedSearch.Code}</code>. Please provide this code to the bot or service requesting it to import your item tracker information.")
            else:
                randCode = randomCode(6)
                if not ItemTracker.query.filter(ItemTracker.Code == randCode).first():
                    new_entry = ItemTracker(Code = randCode, ItemList = str(code)) # type: ignore
                    db.session.add(new_entry)
                    db.session.commit()
                    flash(f"Your upload code is: <code>{randCode}</code>. Please provide this code to the bot or service requesting it to import your item tracker information.")
                else:
                    flash("Something went wrong, please try again.")
    sortedItems = {}
    idToCrateList = {}
    items: List[Item] = Item.query.filter(
        not_(or_(col.contains("Repeat Appearance") for col in TagCols)) #type:ignore
    ).order_by(Item.ItemOrder).all()
    count = len(items)
    crateList: List[Crate] = Crate.query.order_by(Crate.id).all()
    for crate in crateList:
        itemNames = []
        for item in items:
            name = item.ItemName
            if item.ItemNameHTML in itemNames or "(" in item.ItemName:
                name = item.ItemName
            else:
                name= item.ItemNameHTML
                itemNames.append(item.ItemNameHTML)
            formattedItem = {
                "Name" : name,
                "id" : item.id,
                "Tags" : [tag for tag in [item.TagPrimary, item.TagSecondary, item.TagTertiary, item.TagQuaternary, item.TagQuinary, item.TagSeptenary, item.TagSenary] if tag],
                "ImageType" : item.ImageType if item.ImageType else ""
            }
            if int(item.CrateID) == int(crate.id):
                if crate.CrateName in sortedItems:
                    idToCrateList[crate.CrateName].append(item.id)
                    sortedItems[crate.CrateName].append(formattedItem)
                else:
                    idToCrateList[crate.CrateName] = [item.id]
                    sortedItems[crate.CrateName] = [formattedItem]
    return render_template("public/newtracker.html", sortedItems = sortedItems, idCrateList = idToCrateList, validTags = c.validTags, page="newtracker", count=count)


@app.route('/miscitemtracker', methods=('GET', 'POST'))
def miscitemtracker():
    if request.method == 'POST':
        code = json.loads(request.form['importCode'])
        if len(code) < 1:
            flash("Code must have at least one item to upload.")
        else:
            attemptedSearch = ItemTracker.query.filter(ItemTracker.ItemList == str(code)).first()
            if attemptedSearch:
                flash(f"Your upload code is: <code>{attemptedSearch.Code}</code>. Please provide this code to the bot or service requesting it to import your item tracker information.")
            else:
                randCode = randomCode(6)
                if not ItemTracker.query.filter(ItemTracker.Code == randCode).first():
                    new_entry = ItemTracker(Code = randCode, ItemList = str(code)) # type: ignore
                    db.session.add(new_entry)
                    db.session.commit()
                    flash(f"Your upload code is: <code>{randCode}</code>. Please provide this code to the bot or service requesting it to import your item tracker information.")
                else:
                    flash("Something went wrong, please try again.")
    sortedItems = {}
    idToCrateList = {}
    items: List[MiscellaneousItem] = MiscellaneousItem.query.order_by(MiscellaneousItem.ItemOrder).all()
    count = len(items)
    
    groupList: List[MiscellaneousGroup] = MiscellaneousGroup.query.order_by(MiscellaneousGroup.GroupOrder).all()
    groupTypes = []
    for group in groupList:
        if group.GroupType not in groupTypes:
            groupTypes.append(group.GroupType)
        itemNames = []
        for item in items:
            name = item.ItemName
            #if item.ItemNameHTML in itemNames:
            #    name = item.ItemName
            #else:
            #    name= item.ItemNameHTML
            #    itemNames.append(item.ItemNameHTML)
            formattedItem = {
                "Name" : name,
                "id" : item.id,
                "Tags" : [group.GroupType],
                "ImageType" : item.ImageType if item.ImageType else ""
            }
            if int(item.GroupID) == int(group.id):
                if group.GroupName in sortedItems:
                    idToCrateList[group.GroupName].append(item.id)
                    sortedItems[group.GroupName].append(formattedItem)
                else:
                    idToCrateList[group.GroupName] = [item.id]
                    sortedItems[group.GroupName] = [formattedItem]
    return render_template("public/newtracker.html", sortedItems = sortedItems, idCrateList = idToCrateList, validTags = groupTypes, page="miscitemtracker", count=count)



@app.route('/jobspayouts')
def jobspayouts():
    return render_template("public/jobspayout.html", Info = jobsInfo, Secrets = JobsSecrets)

@app.route('/staffcalc')
def staffJobsCalc():
    return render_template("public/staffCalc.html", Info = jobsInfo, Secrets = JobsSecrets)

@app.route('/blockspeed')
def blockspeed():
    sortedItems = {
        "Pickaxe" : [],
        "Axe" : [],
        "Hoe" : [],
        "Shovel" : [],
        "Shears" : []}
    fullList = []
    items: List[Item] = Item.query.filter(
        and_(
            not_(or_(col.contains("Repeat Appearance") for col in TagCols)), #type:ignore
            or_(
                or_(col.contains("Pickaxe") for col in TagCols),#type: ignore
                or_(col.contains("Axe") for col in TagCols),#type: ignore
                or_(col.contains("Hoe") for col in TagCols),#type: ignore
                or_(col.contains("Shovel") for col in TagCols), #type: ignore
                or_(col.contains("Shears") for col in TagCols), # type: ignore
            ))).order_by(Item.ItemOrder).all()
    toolSpeeds = {
        "golden" : 12,
        "netherite" : 9,
        "diamond" : 8,
        "iron" : 6,
        "copper" : 5,
        "stone" : 4,
        "wooden" : 2
    }
    for item in items:
        breakSpeed = 1
        for material, speed in toolSpeeds.items():
            if material in json.loads(item.RawData)["id"]:
                breakSpeed = speed
            if "Shears" in [item.TagPrimary, item.TagSecondary, item.TagTertiary, item.TagQuaternary, item.TagQuaternary]:
                breakSpeed = 2
        
        
        
        
        fullList.append({ "name": item.ItemName, "efficiency" : item.EfficiencyLevel, "submerged_mining_speed" : item.SubmergedMiningSpeedAttribute, "speed" : breakSpeed})
        toolTypes = list(set([item.TagPrimary, item.TagSecondary, item.TagTertiary, item.TagQuaternary, item.TagQuaternary]).intersection(set(["Pickaxe", "Axe", "Hoe", "Shovel", "Shears"])))
        for type in toolTypes:
            sortedItems[type].append({ "name": item.ItemName, "efficiency" : item.EfficiencyLevel, "submerged_mining_speed" : item.SubmergedMiningSpeedAttribute, "speed" : breakSpeed})
        
    return render_template("public/blockbreakspeed.html", itemList = sortedItems, fullList = fullList, blocksToCalculate = c.blocksForBreakSpeedCalculator)

@app.route('/sets')
def sets():
    sets: List[ItemSets] = ItemSets.query.all()
    sortedSets = {"" : []}
    for setType in c.validSetTypes:
        sortedSets[setType] = []
    for set in sets:
        sortedSets[set.Type].append(set)
    return render_template("public/sets.html", sets = sortedSets)

@app.route('/set/<setID>')
def singleSet(setID):
    set: ItemSets | None = ItemSets.query.filter(ItemSets.id == setID).first()
    if not set:
        flash("That set does not exist. Try again some other day.")
        return redirect('/sets')
    items: List[Item] = Item.query.filter(Item.id.in_(json.loads(set.ItemList))).all()
    return render_template("public/set.html", Items = items, set = set)

@app.route('/inventory', methods=['POST', 'GET']) # type: ignore
def inventory():
    items: List[Item] = Item.query.all()
    
    formattedItems = []
    blankSlot = f"""<img height='44' width='44' src="{url_for('static', filename = f"images/{server_name}_Icons/0.png")}">"""
    for item in items:
        hoverableHTML = f"""<img height='44' width='44' src="{url_for('static', filename = f"images/{server_name}_Icons/{item.id}.{item.ImageType}")}" data-bs-custom-class="wide-tooltip" data-bs-toggle="tooltip" data-bs-html="true" data-bs-placement="bottom" data-bs-title="<div class='give-preview-text-outer marker'><div class='give-preview-text w-100'><div class='give-preview-text-inner text-start'>{item.ItemHTML.replace('"', '&quot;')}</div></div></div>">"""
        formattedItems.append({
            "Name" : item.ItemName,
            "HTML" : hoverableHTML,
            "Tags" : [tag for tag in [item.TagPrimary, item.TagSecondary, item.TagTertiary, item.TagQuaternary, item.TagQuinary, item.TagSeptenary, item.TagSenary] if tag]
        })
    return render_template("public/inventory.html", items = formattedItems, validTags = c.validTags, blankSlot = blankSlot)


@app.route('/gamble', methods=['POST', 'GET'])
def gamble():
    amount = request.form.get('amount')
    if not amount: amount = 1
    amount = int(amount)
    if platform != "win32" and amount > 1000: amount = 1000
    crate = request.form.get("crate")
    if not crate or crate == "all":
        crate = "all"
        items = Item.query.order_by(Item.ItemOrder).all()
    else:
        try:
            crate = str(crate)
            items = Item.query.filter_by(CrateID = crate).order_by(Item.ItemOrder).all()
        except:
            items = [c.errorMaker(404)]
    cleanItems = []
    cleanWeights = []
    invalidValues = [None, 0, '']
    for item in items:
        if item.WinPercentage in invalidValues : # type: ignore
            continue
        else:
            cleanItems.append(item)
            cleanWeights.append(float(item.WinPercentage)) # type: ignore
    items = choices(cleanItems, cleanWeights, k = amount)
    
    resultCrates = list(set([int(item.CrateID) for item in items]))
    resultCrates.sort()
    stats = {}
    for resultCrate in resultCrates:
        res = str(resultCrate)
        resultCrate = Crate.query.filter_by(id = resultCrate).one().CrateName
        stats[resultCrate] = {}
        for item in items:
            if item.CrateID == res:
                if item.ItemNameHTML not in stats[resultCrate].keys():
                    stats[resultCrate][item.ItemNameHTML] = 1
                else:
                    stats[resultCrate][item.ItemNameHTML] += 1
        stats[resultCrate] = {k: v for k,v in sorted(stats[resultCrate].items(), key=lambda i: i[1])}
    return render_template("public/gamble.html", Items = items, amount = amount, recentCrate = crate, stats = stats)

@app.route('/apidocs')
def apidocs():
    return render_template("public/api.html")