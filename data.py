from bs4 import BeautifulSoup
import re
import csv

with open("courses.html") as fp:
    soup = BeautifulSoup(fp, features='lxml')


ARCH = {426, 431, 433, 483, 484, 526, 533, 534, 536}
AI = {440, 441, 442, 443, 444, 445, 446, 447, 448, 540, 542, 543, 544, 545, 546, 588}
BIOINFO = {466, 581, 582}
CSED = {500}
DATABASE = {410, 411, 412, 470, 510, 511, 512, 514}
INTERACTIVE_COMPUTING = {409, 415, 416, 417, 418, 419, 445, 465, 467, 469, 519, 565, 567, 568}
PROGRAMMING_LANGUAGES = {421, 422, 427, 428, 474, 475, 476, 477, 521, 522, 524, 527, 576, 584}
SCICOMPUTING = {450, 482, 554, 555, 556, 558}
SECPRIVACY = {461, 463, 562, 563}
SYSNETWORKING = {414, 423, 424, 425, 434, 435, 436, 437, 438, 439, 461, 463, 523, 525, 537, 538, 541, 563}
THEORETICAL = {473, 475, 507, 571, 573, 574, 579, 580, 583, 586}

def assign_category(course_number):
    if course_number in ARCH:
        return "Architecture, Compilers, Parallel Computing"
    elif course_number in AI:
        return "Artificial Intelligence"
    elif course_number in BIOINFO:
        return "Bioinformatics and Computational Biology"
    elif course_number in CSED:
        return "Computers and Education"
    elif course_number in DATABASE:
        return "Database and Information Systems"
    elif course_number in INTERACTIVE_COMPUTING:
        return "Interactive Computing"
    elif course_number in PROGRAMMING_LANGUAGES:
        return "Programming Languages, Formal Methods, Software Engineering"
    elif course_number in SCICOMPUTING:
        return "Scientific Computing"
    elif course_number in SECPRIVACY:
        return "Security and Privacy"
    elif course_number in SYSNETWORKING:
        return "Systems and Networking"
    elif course_number in THEORETICAL:
        return "Theoretical Computer Science"
    else:
        return "N/A"



def parse_block(course_block):

    input_string = course_block.a.text

    formatted_string = " ".join(input_string.split())

    course_number_match = re.match(r"CS\s*\d+", formatted_string)
    course_number = course_number_match.group(0).replace(" ", "") if course_number_match else None

    credits_match = re.search(r"credit: (\d+)", formatted_string)
    credits_count = credits_match.group(1) if credits_match else None

    if course_number and credits_count:
        course_name = formatted_string.replace(course_number_match.group(0), "").split("credit:")[0].strip()
    else:
        course_name = None

    if course_number <= 'CS399':
        return None

    category = assign_category(int(course_number[2:]))

    temp = course_block.find('p', class_='courseblockdesc').getText()
    formatted_string = " ".join(temp.split())

    prerequisite_index = formatted_string.find("Prerequisite: ")
    if prerequisite_index != -1:
        prerequisite_content = formatted_string[prerequisite_index + len("Prerequisite:"):].strip()
        formatted_string = formatted_string[:prerequisite_index].strip()
    else:
        prerequisite_content = None

    return course_number, course_name, int(credits_count), course_block.a['href'], formatted_string, prerequisite_content, category



course_list = []
for block in soup.find_all('div', class_='courseblock'):
    temp = parse_block(block)
    if temp is not None:
        course_list.append(temp)


csv_filename = 'courses.csv'

with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    writer.writerow(['course_number', 'course_name', 'credits', 'link', 'description', 'prereq', 'category'])
    
    for row in course_list:
        writer.writerow(row)

print(f"Data has been written to {csv_filename}")
    
