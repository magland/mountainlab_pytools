window.MLJobMonitor=MLJobMonitor;

function MLJobMonitor(element) {
    if (!element) element=$('<div />');
    let O=element;
    element.empty();
    O.addJob=function(job_id,info) {
        let W=MLJobWidget();
        m_job_widgets[job_id]=W;
        element.append(W);
        W.setInfo(info);
    };
    O.setJobInfo=function(job_id,info) {
        m_job_widgets[job_id].setInfo(info);
    };
    O.clearJobs=function() {
        element.empty();
        m_job_widgets={};
    };
    let m_job_widgets={};
    return element;
}

function MLJobWidget(element) {
    if (!element) element=$('<div />');
    let O=element;

    element.html(`
        <details>
            <summary>
                <span id=summary></span>
            </summary>
            <p>
            <span id=command></span>
            </p>
            <pre>
            <span id=console_output></span>
            </pre>
        </details>
    `);

    O.setInfo=function(info) {
        m_info=JSON.parse(JSON.stringify(info));
        refresh();
    }
    O.info=function() {
        return JSON.parse(JSON.stringify(m_info));
    }
    O.refresh=function() {
        refresh();
    }
    let m_info={};
    
    function refresh() {
        element.find('#summary').html(`<span style="color:${status_color(m_info.status)}">${m_info.status}</span> ${m_info.processor_name}`);
        element.find('#command').html(`${m_info.command||''}`);
        element.find('#console_output').html(`${m_info.console_output||''}`);
    }
    function status_color(status) {
        if (status=='pending') return 'orange';
        else if (status=='running') return 'magenta';
        else if (status=='finished') return 'green';
        else if (status=='error') return 'red';
        else if (status=='stopped') return 'pink';
        else return 'black';
    }
    
    return element;
    
    
}