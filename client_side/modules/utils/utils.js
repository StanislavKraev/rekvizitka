function x(Y) {
    "use strict";

    // http://studysphere.ru/work.php?id=305
    var _preloadImg = [],
        _morphData = {'компания':{
            //     >4             1          2..4
                'i':['компаний', 'компания', 'компании'],
                'r':['компаний', 'компании', 'компаний'],
                'd':['компаниям', 'компании', 'компаниям'],
                'v':['компаний', 'компанию', 'компании'],
                't':['компаниями', 'компанией', 'компаниями'],
                'p':['компаниях', 'компании', 'компаниях']
            },
            'диалог' : {
                'i' : [ "диалогов", "диалог", "диалога" ]
            },
            'контрагент' : {
                'i' : [ "контрагентов", "контрагент", "контрагента" ]
            },
            'заявка' : {
                'i' : [ "заявок", "заявка", "заявки" ],
                'r' : [ "заявок", "заявку", "заявки" ],
                'v' : [ "заявок", "заявку", "заявки" ]
            },
            'dialog' : {
                'i' : [ "dialogs", "dialog", "dialogs" ]
            }
        },
    //                          1, 21, 31... 2,3,...,11,12,...
        _morphVerbData = {'давать':{
            'b':['даст', 'дадут'],
            'n':['дает', 'дают'],
            'p':['дал', 'дали']
        }};

    Y.utils = {

//        idEmptyObject:function(obj){
//            var i;
//            for (i in obj){
//                return false;
//            }
//            return true;
//        },

        getURLparams: function() {
            var vars = [], hash, i,
                hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');

            for(i = 0; i < hashes.length; i+=1)
            {
                hash = hashes[i].split('=');
                vars.push(hash[0]);
                vars[hash[0]] = hash[1];
            }
            return vars;
        },

        getURLparam: function(name, type) {
            var paramVal = null, hash, i,
                hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&'),
                paramType = type || 'string';

            for(i = 0; i < hashes.length; i += 1) {
                hash = hashes[i].split('=');

                if(name === hash[0]) {
                    switch(paramType) {
                        case 'string':
                            paramVal = hash[1] || '';
                            break;
                        case 'number':
                            paramVal = parseInt(hash[1], 10);
                            break;
                    }
                    break;
                }
            }
            return paramVal;
        },
        
        is_function:function (obj) {
            return typeof(obj) === 'function';
        },

        morph:function (word, count, pad) {
            var words;

            function declination(a, b, c, s) {

                var words = [a, b, c], index;
                index = s % 100;

                if (index >= 11 && index <= 14) {
                    index = 0;
                }
                else {
                    index = (index %= 10) < 5 ? (index > 2 ? 2 : index) : 0;
                }

                return(words[index]);
            }

            if (_morphData.hasOwnProperty(word) && _morphData[word].hasOwnProperty(pad)) {
                words = _morphData[word][pad];
                return declination(words[0], words[1], words[2], count);
            }
            return "";
        },

        morph_verb:function (verb, count, tense) {
            var words = _morphVerbData[verb], countStr = count.toString();
            if ((countStr[countStr.length - 1] === '1') && (count !== 11)) {
                return words[tense][0];
            }
            return words[tense][1];
        },

        latestVersionName:function (moduleName) {
            var mod, maxVer = "", ver, all = YUI_config.groups.rek.modules;

            for (mod in all) {
                if (all.hasOwnProperty(mod)) {
                    if (mod.indexOf(moduleName + '/') === 0) {
                        ver = mod.slice(moduleName.length + 1, mod.length);
                        if (ver > maxVer) {
                            maxVer = ver;
                        }
                    }
                }
            }
            if (!maxVer.length) {
                return moduleName;
            }
            return moduleName + '/' + maxVer;
        },

        getCookie:function (name) {
            var cookieValue = null,
                cookies,
                cookie,
                i;

            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                for (i = 0; i < cookies.length; i += 1) {
                    cookie = jQuery.trim(cookies[i]);

                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        setCookie : function(name, value, props) {
            var exp, d, propName, propValue, updatedCookie;
            props = props || {};
            exp = props.expires;

            if (typeof exp === "number" && exp) {
                d = new Date();
                d.setTime(d.getTime() + exp * 1000);
                exp = props.expires = d;
            }
            if(exp && exp.toUTCString) {
                props.expires = exp.toUTCString();
            }

            value = encodeURIComponent(value);
            updatedCookie = name + "=" + value;
            for(propName in props){
                if (props.hasOwnProperty(propName)) {
                    updatedCookie += "; " + propName;
                    propValue = props[propName];
                    if(propValue !== true){
                        updatedCookie += "=" + propValue;
                    }
                }
            }
            document.cookie = updatedCookie;
        },

        bytesToHumanReadable:function (bytes, precision) {
            var kilobyte = 1024,
                megabyte = kilobyte * 1024,
                gigabyte = megabyte * 1024,
                terabyte = gigabyte * 1024;

            if ((bytes >= 0) && (bytes < kilobyte)) {
                return bytes + ' B';

            } else if ((bytes >= kilobyte) && (bytes < megabyte)) {
                return (bytes / kilobyte).toFixed(precision) + ' KB';

            } else if ((bytes >= megabyte) && (bytes < gigabyte)) {
                return (bytes / megabyte).toFixed(precision) + ' MB';

            } else if ((bytes >= gigabyte) && (bytes < terabyte)) {
                return (bytes / gigabyte).toFixed(precision) + ' GB';

            } else if (bytes >= terabyte) {
                return (bytes / terabyte).toFixed(precision) + ' TB';

            } else {
                return bytes + ' B';
            }
        },
        preloadImages:function () {
            var i, id;
            for (i = 0; i < arguments.length; i += 1) {
                id = _preloadImg.length;
                _preloadImg[id] = new Image();
                _preloadImg[id].src = arguments[i];
            }
        },
        getInternetExplorerVersion:function () {
            var rv = -1,
                ua,
                re; // Return value assumes failure.
            if (navigator.appName === 'Microsoft Internet Explorer') {
                ua = navigator.userAgent;
                re = new RegExp("MSIE ([0-9]{1,}[\\.0-9]{0,})");
                if (re.exec(ua) !== null) {
                    rv = parseFloat(RegExp.$1);
                }
            }
            return rv;
        },
        capitaliseFirstLetter:function (val) {
            return val.charAt(0).toUpperCase() + val.slice(1);
        },
        is_correct_email:function (email) {
            var errors = [], regexp = /^[a-zA-Z0-9._\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,4}$/;
            if (email.length > 255) {
                errors[errors.length] = "Превышено допустимое количество символов (255)";
            }
            if (!regexp.test(email.trim())) {
                errors[errors.length] = "Некорректный формат адреса электронной почты";
            }
            return errors;
        },

        isEmpty:function (str) {
            return (str === null) || (str.length === 0);
        },

        isEmail:function (str) {
            var re = new RegExp(/^[^\s()<>@,;:\/]+@\w[\w\.\-]+\.[a-z]{2,}$/i); // lint wants escaped '-'
            if (this.isEmpty(str)) {return false;}
            return re.test(str);
        },

        fillEmptyProps:function (obj, emptyPropsNames) {
            var i;
            for (i = 0; i < emptyPropsNames.length; i += 1) {
                obj[emptyPropsNames[i]] = '';
            }
        },
        wrapEachLine:function (substring, firstTag, lastTag) {
            var arr, arr2 = [], i;
            arr = substring.split(/\r\n|\r|\n/);
            for (i in arr) {
                if (arr.hasOwnProperty(i)) {
                    arr2.push(arr[i]);
                }
            }
            return firstTag + arr2.join(lastTag+firstTag) + lastTag;
        },
        escapeStr : function(str) {
            var escapeTemplateFunc = _.template("<%-data%>");
            return escapeTemplateFunc({data : str});
        },
        makeShortDateString : function(date) {
            var monthnames = Y.Locales['utils'].months_gen, reztstr;
            reztstr = date.getDate() + " " + monthnames[date.getMonth()] + " " +
                    date.getFullYear() + " " + this.formatNumber(date.getHours(), 2) +
                       ":" + this.formatNumber(date.getMinutes(), 2);
            return reztstr;
        },
        formatNumber : function(num, len) {
            var reztstr = String(num);
            while(reztstr.length < len) {
                reztstr = '0' + reztstr;
            }
            return reztstr;
        },
        makeDateString : function(date) {
            return this.formatNumber(date.getDate(), 2) + '.' +
                    this.formatNumber(date.getMonth() + 1, 2) + '.' + date.getFullYear();
        },
        makeHourMinString : function(date) {
            return this.formatNumber(date.getHours(), 2) + ':' +
                    this.formatNumber(date.getMinutes(), 2);
        },
        stringToDate : function(str) {
            var rezt = new Date(str), tmpStr, noGmtStr;
            if(isNaN(rezt.getTime())) {  // Opera or IE
                tmpStr = str.replace(/\.\d+/, ' ').replace('T', ' ');  // for Opera and IE
                rezt = new Date(tmpStr);
                if(isNaN(rezt.getTime())) {  // IE (without GMT)
                    noGmtStr = tmpStr.substring(0, tmpStr.lastIndexOf(' ')).replace(/-/g, '/');
                    // todo: process the date with GMT for IE
                    rezt = new Date(noGmtStr);
                }
            }
            return rezt;
        },
        cutLongString : function(str, len) { // todo: предусмотреть строки под escape
            var rezt;
            if(str.length > len + 2) {
                rezt = str.substring(0, len).replace(/[\s!-\/:-@\[-`{-~]+$/, '');
                if(rezt.length < 1) {
                    rezt = str.substring(0, len).replace(/\s+$/, '');
                }
                rezt += '...';
            } else {
                rezt = str;
            }
            return rezt;
        },
        insertCaretReturns : function(text) {
            return text.replace(/\r\n|\r|\n/g, '<br/>');
        },
        markLinksForHtml : function(text) {
            var notags = text.replace(/</g, '&lt;').replace(/>/g, '&gt;'),
                result = notags.replace(/((http|ftp):\/\/[^\s">]+[\w\d\?\/])/g, '<a href="$1" target="_blank">$1</a>');
            return this.escapeTextWithTags(result, [ "a" ]).replace(/&amp;/g, '&');
        },
        escapeTextWithTags : function(text, tagArray) {
            var result = '', startIndex, textTail = text, tagArr = tagArray || [], subTagArr,
                i, testIndex, foundTag, endIndex, finishTagText, startTagText, startTagSelector,
                innerText, tagPos;
            if(tagArr.length < 1) {
                result = this.escapeStr(text);
            } else {
                while(textTail.length > 0) {
                    startIndex = -1;
                    for(i = 0; i < tagArr.length; i += 1) {
                        testIndex = textTail.indexOf('<' + tagArr[i] + ' ');
                        if(testIndex === -1) {
                            testIndex = textTail.indexOf('<' + tagArr[i] + '>');
                        }

                        if(testIndex !== -1) {
                            if(startIndex === -1 || testIndex < startIndex) {
                                startIndex = testIndex;
                                foundTag = tagArr[i];
                                tagPos = i;
                            }
                        }
                    }
                    if(startIndex !== -1) {
                        result += this.escapeStr(textTail.substring(0, startIndex));
                        finishTagText = '</' + foundTag + '>';
                        startTagSelector = new RegExp("(<" + foundTag + ">|<" + foundTag + "\\s+[^>]+>)", "i");
                        startTagText = textTail.substring(startIndex, textTail.length)
                                                  .match(startTagSelector)[0];
                        result += startTagText;
                        endIndex = textTail.indexOf(finishTagText, startIndex + startTagText.length);
                        if(endIndex === -1) {
                            endIndex = textTail.length;
                        }
                        innerText = textTail.substring(startIndex + startTagText.length, endIndex);
                        subTagArr = tagArray.slice(0, tagArray.length);
                        subTagArr.splice(tagPos, 1);
                        result += this.escapeTextWithTags(innerText, subTagArr);
                        result += finishTagText;
                        textTail = textTail.substring(endIndex + finishTagText.length, textTail.length);
                    } else {
                        result += this.escapeStr(textTail);
                        textTail = '';
                    }
                }
            }
            return this.insertCaretReturns(result);
        },
        cutAndEscapeMultilineText : function(text, maxLines, maxCharPerLine) {
            // return text.substring(0, maxLines * maxCharPerLine);
            var textBred = this.insertCaretReturns(text),
                textLines = textBred.split('<br/>'),
                resultLines = [], i;

            for(i = 0; i < textLines.length && i < maxLines; i += 1) {
                if(textLines[i].length > maxCharPerLine) {
                    resultLines.push(this.escapeStr(textLines[i].substring(0, (maxLines - i) * maxCharPerLine)) + '...');
                    break;
                }
                resultLines.push(this.escapeStr(textLines[i]));
            }
            return resultLines.join('<br/>');
        }
    };
}