function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function createNewJob() {
    const fadeTime = 400;

    $('#create-job').fadeOut(fadeTime);
    await sleep(fadeTime);
    $('#wait-job').fadeIn(fadeTime)
    await sleep(fadeTime);

    for(let i = 0; i <= 100; i += 10) {
        $('#progress-bar').width(i + '%');
        await sleep(300);
    }
    $('#progress-bar').addClass('bg-success');
    
    await sleep(400);

    $('#wait-job').fadeOut(fadeTime);
    await sleep(fadeTime);
    $('#results').fadeIn(fadeTime);

    return false;
}