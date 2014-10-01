function comparisonSettings($dialog, group) {
    var $body = $dialog.find('.modal-body');
    var url = '/rest/settings/group';
    if (group != '') {
        url += '/' + group;
    }
    var settingInputs = {};
    $.getJSON(url).done(function (data) {
        for (var i in data) {
            var $group = $('<div class="form-group"/>');
            $group.append($('<label class="control-label" for="setting-' + i + '">' + i + '</label>'));
            var $input = $('<input class="form-control" id="setting-' + i + '"/>');
            $group.append($input.val(data[i]));
            $body.append($group);
            settingInputs[i] = $input[0];
        }
        $dialog.find('.btn-primary').click(function () {
            var data = {};
            for (var i in settingInputs) {
                data[i] = settingInputs[i].value;
            }
            $.ajax({url: url, type: 'PUT', data: data});
        });
    });
    $dialog.modal();
}

function observerSettings($dialog, group) {
    var $table = $('<table class="table"/>');

    var $newEmail = $('<input class="form-control" placeholder="Enter email" id="observers-add-email"/>');
    var $tr = $('<tr/>');
    $tr.append($('<td/>').append($('<label class="sr-only" for="observers-add-email">E-mail</label>')).append($newEmail));
    var $btn = $('<button class="btn">Add</button>').click(function () {
        var newEmail = $newEmail[0].value;
        $.getJSON('/rest/alerts/add', {email: newEmail, path: group});
        $tr = $('<tr/>');
        $tr.append($('<td><a href="mailto:' + newEmail + '">' + newEmail + '</a><span></span></td>')).
            append($('<td/>').append(createRemoveButton(newEmail)));
        $table.append($tr);
    });
    $tr.append($('<td/>').append($btn));
    $table.append($tr);

    var url = '/rest/alerts/list';
    if (group != '') {
        url += '/' + group;
    }

    function createRemoveButton(email) {
        var $btn = $('<button class="btn">Remove</button>').click(function () {
            $.getJSON('/rest/alerts/remove', {email: email, path: group});
            $btn.parent().parent().remove();
        });
        return $btn;
    }

    $.getJSON(url).done(function (data) {
        for (var i = 0; i < data.length; ++i) {
            var via = '';
            if (data[i][1] != group) {
                via = 'via ';
                if (data[i][1] == '') {
                    via += "&lt;root&gt;"
                }
                else {
                    via += data[i][1];
                }
            }
            $tr = $('<tr/>');
            $tr.append($('<td><a href="mailto:' + data[i][0] + '">' + data[i][0] + '</a> <small>' + via + '</small></td>')).
                append($('<td/>').append(createRemoveButton(data[i][0])));
            $table.append($tr);
        }
    });
    $dialog.find('.modal-body').empty().append($table);
    $dialog.modal();
}
