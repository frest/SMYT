function submitField(selector) {
    value = $(selector).val();
    input = $(selector);
    td = $(selector).parent();
    if ( input.valid() ) {
        $.notify('Данные корректны', 'success');
        params = td.attr('id').split('-');
        data = {
            field: params[1],
            value: value,
        };
        $.ajax({
            type: "POST",
            url: "/dynamic/update/" + model_active + "/" + params[0] + "/",
            datatype: "json",
            data: data,
            success: function(data) {
                $.notify(data['message']['text'], data['message']['status']);
                span = '<span class="field">' + value + '</span>';
                td.html(span);
                field_active = false;
            },
            error: function(data) {
               $.notify('Ошибка связи с сервером', 'error'); 
            }

        });
    } else {
        $.notify('Данные не корректны', 'error');
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length+1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function renderTable(data) {
    $('.table > tbody').html('<tr><th>ID</th></tr>');
    for (var field in data['fields']) {
        $('.table  tr').append('<th>' + data['fields'][field][0] + '</th>');
    }
    $('.table  tr').append('<th>Удалить</th>');
    for (var model in data['models']) {
        pk = data['models'][model]['pk'];
        $('.table > tbody').append('<tr><td>' + pk + '</td></tr>');
        for (field in data['fields']) {
            td = '<td id="' + [pk, field].join('-') + '" type="' + data['fields'][field][1]; 
            td += '"><span class="field">' + data['models'][model]['fields'][field] + '</span></td>';
            $('.table tr:last').append(td);
        }
        td = '<td pk="' + pk + '"><span class="glyphicon glyphicon-remove remove"></span></td>'
        $('.table tr:last').append(td);
    }
}

function toggleActive(model) {
    $('.model#model-' + model_active).toggleClass('active');
    $('.model#model-' + model).toggleClass('active');
    model_active = model;
}

function renderForm(data) {
    for (var field in data['fields']) {
        field_id = data['fields'][field];
        field_class = 'string';
        (field_id[1] == 'IntegerField') ? field_class = 'integer' : true;
        (field_id[1] == 'DateField') ? field_class = 'date' : true;
        field_block = '<div class="form-group"><label for="' + field + '">' + field_id[0];
        field_block += ': </label><input type="text" value="" id="' + field + '" name="' + field;
        field_block += '" class="form-control ' + field_class + '"/></div>';
        $('.form').append(field_block);
    }
    $('.form').append('<input type="submit" class="btn btn-primary" value="Добавить">');
    $('.date').datepicker({dateFormat: "yy-mm-dd"});
}

$(document).ready(function(e) {
    $.validator.addClassRules({
        string: {
            required: true,
        },
        integer: {
            required: true,
            digits: true,
        },
        date: {
            required: true,
            dateISO: true,
        },
    });
    $.validator['messages']['digits'] = 'Поле может содержать только числа';
    $.validator['messages']['required'] = 'Это поле не может быть пустым';
    $.validator['messages']['dateISO'] = 'Введите корректную дату';
    model_active = '';
    field_active = false;


    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if ( !(settings.type in ['GET', 'HEAD', 'OPTIONS', 'TRACE'])) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('.model:first').click();
}).on("click", ".model", function(e) {
    model = $(this).attr('id').split('-')[1];
    url = '/dynamic/table/' + model;
    $.ajax({
        type: "GET",
        url: url,
        success: function(data) {
            toggleActive(model);
            renderTable(data);
            renderForm(data);
            field_active = false;
            $.notify(data['message']['text'], data['message']['status']);
        }
    });
}).on("click", ".field", function(e) {
    if (! field_active) {
        td = $(this).parent();
        value = $(this).html();
        input = '<input class="edit" type="text" name="edit" value="' + value + '" />';
        td.html(input);
        switch(td.attr('type')){
            case 'IntegerField':
                td.children('.edit').addClass('integer');
                break;
            case 'DateField':
                td.children('.edit').addClass('date');
                td.children('.date').toggleClass('edit');
                $('.date').datepicker({dateFormat: "yy-mm-dd", onClose: function() {
                    submitField('td .date');
                }});
                break;
            default:
                td.children('.edit').addClass('string');
        }
        td.children('.edit, .date').focus();
        field_active = true;
    }

}).on("focusout", ".edit", function(e) {
    submitField('.edit');

}).on("submit", ".form", function(e) {
    form = $(this);

    data = form.serializeArray();
    if (form.valid()) {
        $.ajax({
            url: "/dynamic/create/" + model_active + "/",
            type: 'POST',
            data: data,
            success: function(data) {
                $.notify(data['message']['text'], data['message']['status']);
            },
            error: function() {
                $.notify('Error', 'error');
            }
        });
        $('.model#model-' + model_active).click();
    }
    e.preventDefault();

}).on("click", ".remove", function(e) {
    td = $(this).parent();
    pk = td.attr('pk');
    $.ajax({
        url: "/dynamic/delete/" + model_active + "/" + pk + "/",
        type: 'POST',
        success: function(data) {
            $.notify(data['message']['text'], data['message']['status']);
        },
        error: function() {
            $.notify('Error', 'error');
        }
    });
    $('.model#model-' + model_active).click();
});
