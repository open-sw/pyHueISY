function filter_select(event, type_id) {
    document.getElementById(type_id).textContent = triggerTypes[event.target.value]["type_desc"];
}

function addTrigger()
{
    var elemNewRow = document.getElementById("trigger-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);
    elemInsertRow.removeAttribute("id");

    nTriggers += 1;

    var elemOrigSelect = elemNewRow.getElementsByTagName("select")[0];

    var elem = elemInsertRow.getElementsByTagName("input")[0];

    elem.id = "remove-trigger-" + nTriggers;
    elem.className = "delete-button";
    elem.onclick = removeTrigger;

    elem = elemInsertRow.getElementsByTagName("select")[0];
    elem.id = "trigger-" + nTriggers;
    elem.name = "trigger[" + nTriggers + "]";
    elem.selectedIndex = elemOrigSelect.selectedIndex;
    elem.onchange = new Function("event", "filter_select(event, \"trigger-" + nTriggers + "-type\")");

    elem = elemInsertRow.getElementsByTagName("span")[0];
    elem.id = "trigger-" + nTriggers + "-type"

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);
}

function removeTrigger(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);
    }
}

function addScene()
{
    var elemNewRow = document.getElementById("scene-new-row");
    var elemInsertRow = elemNewRow.cloneNode(true);

    nScenes += 1;

    var elemOrigSelect = elemNewRow.getElementsByTagName("select")[0];

    elemInsertRow.removeAttribute("id");

    var elemSelect = elemInsertRow.getElementsByTagName("select")[0];
    var elemTDList = elemInsertRow.getElementsByTagName("td");

    elemSelect.id = "scene-" + nScenes;
    elemSelect.name = "scene[" + nScenes + "]";
    elemSelect.selectedIndex = elemOrigSelect.selectedIndex;

    var elemInput = elemInsertRow.getElementsByTagName("input")[0];

    elemInput.id = "remove-scene-" + nScenes;
    elemInput.className = "delete-button";
    elemInput.onclick = removeScene;

    var elemMoveUp = document.createElement('input');
    elemMoveUp.id = "move-scene-up-" + nScenes;
    elemMoveUp.className = "move-up-button";
    elemMoveUp.setAttribute("type", "button");
    elemMoveUp.onclick = moveUpScene;

    var elemMoveUpDiv = document.createElement("div");
    elemMoveUpDiv.appendChild(elemMoveUp);
    elemTDList[1].appendChild(elemMoveUpDiv);

    var elemMoveDown = document.createElement('input');
    elemMoveDown.id = "move-scene-down-" + nScenes;
    elemMoveDown.className = "move-down-button";
    elemMoveDown.setAttribute("type", "button");
    elemMoveDown.onclick = moveDownScene;

    var elemMoveDownDiv = document.createElement("div");
    elemMoveDownDiv.appendChild(elemMoveDown);
    elemTDList[2].appendChild(elemMoveDownDiv);

    elemNewRow.parentNode.insertBefore(elemInsertRow, elemNewRow);

    update_move_scene_buttons(elemNewRow.parentNode);
}

function removeScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var tableNode = rowNode.parentNode;

        tableNode.removeChild(rowNode);

        update_move_scene_buttons(tableNode);
    }
}

function update_move_scene_buttons(tableNode) {
    var upButtons = tableNode.getElementsByClassName("move-up-button");
    var index;

    for (index = 0; index < upButtons.length; index++) {
        upButtons[index].disabled = false;
    }
    upButtons[0].disabled = true;

    var downButtons = tableNode.getElementsByClassName("move-down-button");

    for (index = 0; index < upButtons.length; index++) {
        downButtons[index].disabled = false;
    }
    downButtons[downButtons.length - 1].disabled = true;
}

function moveUpScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByTagName("select")[0];

        var prevRowNode;
        for (prevRowNode = rowNode.previousElementSibling; prevRowNode != null; prevRowNode = prevRowNode.previousElementSibling) {
            if (prevRowNode.tagName != null && prevRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (prevRowNode != null) {
            var elemPrevious = prevRowNode.getElementsByTagName("select")[0];

            var indexCurrent = elemCurrent.selectedIndex;
            elemCurrent.selectedIndex = elemPrevious.selectedIndex;
            elemPrevious.selectedIndex = indexCurrent;
        }
    }
}

function moveDownScene(event) {
    var rowNode = getContainingRow(event.target);
    if (rowNode != null) {
        var elemCurrent = rowNode.getElementsByTagName("select")[0];

        var nextRowNode = null;
        for (nextRowNode = rowNode.nextElementSibling; nextRowNode != null; nextRowNode = nextRowNode.nextElementSibling) {
            if (nextRowNode.tagName != null && nextRowNode.tagName.toUpperCase() == "TR") {
                break;
            }
        }

        if (nextRowNode != null) {
            var elemNext = nextRowNode.getElementsByTagName("select")[0];

            var indexCurrent = elemCurrent.selectedIndex;
            elemCurrent.selectedIndex = elemNext.selectedIndex;
            elemNext.selectedIndex = indexCurrent;
        }
    }
}

function getContainingRow(node) {
    var rowNode = null;
    for (rowNode = node.parentNode; rowNode != null; rowNode = rowNode.parentNode) {
        if (rowNode.tagName.toUpperCase() == "TR") {
            break;
        }
    }
    return rowNode;
}
