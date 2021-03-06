function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Creates a new job, waits for the computation to finish and reports back the URL from where
// the results can be downloaded.
async function createNewJob() {
    const fadeTime = 400;
    let result;

    $('#create-job').fadeOut(fadeTime);
    let create_job = await $.get('http://api.cloud.dev.novium.pw/create_job?angle=' + $('#angle-input').val());
    create_job = JSON.parse(create_job);
    
    if(create_job.status != 'done') {
        await sleep(fadeTime);
        $('#wait-job').fadeIn(fadeTime)
        await sleep(fadeTime);

        let result;
        let w = 20;
        while(true) {
            result = await $.get('http://api.cloud.dev.novium.pw/get?id=' + create_job.id);
            result = JSON.parse(result);

            if(result.status == 'created') {
                $('#progress-bar').addClass('bg-secondary');
                $('#progress-bar').width('20%');
            }
            if(result.status == 'computing') {
                if(w < 90) {
                    w += 10;
                }
                
                $('#progress-bar').addClass('bg-warning');
                $('#progress-bar').width(w + '%');
            }
            if(result.status == 'done') {
                break;
            }

            await sleep(1000);
        }
        $('#progress-bar').addClass('bg-success');

        await sleep(400);

        $('#wait-job').fadeOut(fadeTime);
        await sleep(fadeTime);
    } else {
        result = create_job;
    }

    $('#results').fadeIn(fadeTime);
    $('#url').text(result.url);

    return false;
}