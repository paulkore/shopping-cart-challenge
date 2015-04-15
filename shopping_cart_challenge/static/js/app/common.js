String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

String.prototype.contains = function(str) {
    return this.indexOf(str) > -1
};

Array.prototype.last = function(){
    return this[this.length - 1];
};

