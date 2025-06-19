from constants import categories_list
import copy

def parse_linkedin_jobs(jobs):
    """
    return the jobs neatly sorted into categories
    """
    category_jobs = copy.deepcopy(categories_list)

    # for job_list in jobs:
    for job in jobs:
        if "writer" in str(job[0]).lower():
            category_jobs["content writing"].append(job)
        elif "developer" in str(job[0]).lower() or "engineer" in str(job[0]).lower():
            category_jobs["software development"].append(job)
        elif "assistant" in str(job[0]).lower():
            category_jobs["virtual assistant"].append(job)
        elif "customer" in str(job[0]).lower():
            category_jobs["customer service"].append(job)
        elif "data entry" in str(job[0]).lower():
            category_jobs["data entry"].append(job)
        elif "design" in str(job[0]).lower():
            category_jobs["design"].append(job)
        elif "ai engineer" in str(job[0]).lower() or "ml engineer" in str(job[0]).lower():
            category_jobs["ai/ml engineering"].append(job)
        elif "social media" in str(job[0]).lower():
            category_jobs["social media managment"].append(job)
        elif "project manager" in str(job[0]).lower():
            category_jobs["project management"].append(job)
        else:
            category_jobs["others"].append(job)
    
    return category_jobs


def return_unseen_jobs(all_jobs, lw, lng):
    """
    remove jobs seen before
    """
    unseen_jobs = []
    count = 0

    for job_list in all_jobs:
        while (count < len(job_list)) and ((job_list[count][-1] != lw) and (job_list[count][-1] != lng)):
            unseen_jobs.append(job_list[count])
            count += 1
    
    return unseen_jobs
            

def format_text_as_html(text: str):
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        words = line.strip().split()
        if 0 < len(words) < 4:
            html_lines.append(f"<b>{line.strip()}</b>")
        else:
            for word in line.split("."):
                html_lines.append(f"{word}")
            # html_lines.append(f"{line.strip()}\n")
    return "\n".join(html_lines)
