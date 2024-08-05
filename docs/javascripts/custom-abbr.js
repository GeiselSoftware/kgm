function splitAtFirstSpace(text) {
    let index = text.indexOf(' ');  // Find the first space

    if (index === -1) {
	return [text];  // Return the whole string as the only element if no space is found
    }

    let part1 = text.substring(0, index);  // Everything before the space
    let part2 = text.substring(index + 1);  // Everything after the space

    return [part1, part2];
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('abbr').forEach(function(abbr) {
	let [url, tip] = splitAtFirstSpace(abbr.title);
	//console.log("abbr: ", url, tip);
        abbr.outerHTML = '<span class="custom-abbr" style="color: red;">' + '<a href=' + url + ' style="text-decoration: underline; text-decoration-style: dotted; color: black">' + abbr.innerHTML + '</a></span>';
    });
});

