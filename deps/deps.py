from constants import categories_list
import copy

def parse_linkedin_jobs(jobs):
    """
    return the jobs neatly sorted into categories
    """
    category_jobs = copy.deepcopy(categories_list)

    for job_list in jobs:
        for job in job_list:
            if "writer" in str(job[0]).lower():
                category_jobs["content writing"].append(job)
            elif "developer" in str(job[0]).lower():
                category_jobs["software development"].append(job)
            elif "assistant" in str(job[0]).lower():
                category_jobs["virtual assistant"].append(job)
            elif "customer" in str(job[0]).lower():
                category_jobs["customer service"].append(job)
            elif "data entry" in str(job[0]).lower():
                category_jobs["data entry"].append(job)
            elif "design" in str(job[0]).lower():
                category_jobs["design"].append(job)
            elif "ai" in str(job[0]).lower() or "ml" in str(job[0]).lower():
                category_jobs["ai/ml engineering"].append(job)
            elif "social media" in str(job[0]).lower():
                category_jobs["social media managment"].append(job)
            elif "project manager" in str(job[0]).lower():
                category_jobs["project management"].append(job)
            else:
                category_jobs["others"].append(job)
    
    return category_jobs
