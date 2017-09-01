from celery import app
from django.conf import settings

from gitlab_logging.helpers import GitlabIssuesHelper

@app.task
def task_log_gitlab_issue_open(issue_title, issue_content, trace_raw):
    """
    Proceed the issue opening task
    """
    gl = GitlabIssuesHelper.gitlab()

    print("Opening issue: %s..." % issue_title)
    gitlab_issue_labels = ""
    gitlab_issue_title_prefix = ""
    # New Feature: Allows configuration of assigning a
    # prefix to issues created with this module.
    if hasattr(settings, 'GITLAB_ISSUE_TITLE_PREFIX'):
        gitlab_issue_title_prefix = settings.GITLAB_ISSUE_TITLE_PREFIX

    issue_title = gitlab_issue_title_prefix + issue_title

    if hasattr(settings,'GITLAB_ISSUE_LABELS'):
        gitlab_issue_labels = settings.GITLAB_ISSUE_LABELS

    # Create issue with python-gitlab
    response = gl.project_issues.create({
            'title': issue_title,
            'description': issue_content,
            'labels': gitlab_issue_labels
        }, project_id=settings.GITLAB_PROJECT_ID)

    if response:
        issue_id = response.id

        if issue_id:
            print("Issue opened: %s [ID: %s]" % (issue_title, issue_id))

            GitlabIssuesHelper.store_issue(trace_raw, settings.GITLAB_PROJECT_ID, response.id)
    else:
        print("Issue could not be opened: %s" % issue_title)


@app.task
def task_log_gitlab_issue_reopen(issue_id):
    """
    Proceed the issue re-opening task
    """
    print("Re-opening issue [ID: %s]" % issue_id)

    # Update issue with python-gitlab
    issue = gl.project_issues.get(issue_id, project_id=settings.GITLAB_PROJECT_ID)

    issue.state_event = 'reopen'
    success, response = issue.save()

    if success:
        print("Issue re-opened [ID: %s]" % issue_id)
    else:
        print("Issue could not be re-opened [ID: %s]" % issue_id)
