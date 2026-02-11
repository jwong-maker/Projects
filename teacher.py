import extra


def markToGpa(mark): 
    if mark >= 90:
        return 4.0
    elif mark >= 85:
        return 3.7
    elif mark >= 80:
        return 3.3
    elif mark >= 75:
        return 3.0
    elif mark >= 70:
        return 2.7
    elif mark >= 65:
        return 2.3
    elif mark >= 60:
        return 2.0
    elif mark >= 55:
        return 1.7
    elif mark >= 50:
        return 1.3
    else:
        return 0.0

def getValidInput(prompt, minVal, maxVal, inputType=float):
    while True:
        try:
            value = inputType(input(prompt))
            if minVal <= value <= maxVal:
                return value
            print(f"Value must be between {minVal} and {maxVal}")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def calculateSemesterGpa():
    totalQualityPoints = 0
    totalCredits = 0
    
    numSubjects = int(getValidInput("Enter number of subjects: ", 1, 20, int))
    
    for i in range(numSubjects):
        print(f"\nSubject {i+1}:")
        mark = getValidInput("Enter exam marks (0-100): ", 0, 100) 
        
        gpa = markToGpa(mark)
        totalQualityPoints += gpa * 4
        totalCredits += 4

    return totalQualityPoints, totalCredits

def main():
    cumulativeQuality = 0
    cumulativeCredits = 0
    
    while True:
        print("\n=== New Semester ===")
        semQuality, semCredits = calculateSemesterGpa()
        
        # Calculate semester GPA
        sem_gpa = semQuality / semCredits
        print(f"\nSemester GPA: {sem_gpa:.2f}")
        
        # Update cumulative totals
        cumulativeQuality += semQuality
        cumulativeCredits += semCredits
        
        # Calculate CGPA
        cgpa = cumulativeQuality / cumulativeCredits
        print(f"Current CGPA: {cgpa:.2f}")

def changeDataType(dictionary_to_change):
    for i in dictionary_to_change:
        found_symbol = False
        if "@" in i: found_symbol = True

        if not found_symbol:
            try:
                int(dictionary_to_change[i])
            except (ValueError, TypeError):
                pass
            else:
                dictionary_to_change[i] = int(dictionary_to_change[i])

def readRecord(dictionary, header, lines, includeID):
    success = True
    if len(lines) < 1:
        success = False
        return success, "No data found in database"

    increment = 1
    increment += len(header)-len(lines[0].strip().strip("\n").split(","))

    for i in range(0, len(lines), increment):
        line = lines[i]
        attributes = line.strip().split(",", len(header)-1)

        if includeID == True:
            row_dict = {header[i]: attributes[i] for i in range(0, len(attributes))}
        else:
            row_dict = {header[i]: attributes[i] for i in range(1, len(attributes))}

        for j in range(1, increment):
            extraCount = j + i
            extraLine = lines[extraCount]

            extraLine_attributes = extraLine.strip().split(",")

            if extraLine_attributes[0] in header:
                current_header = header[len(attributes) + j - 1]
                found_list = []

                for l in range(1, len(extraLine_attributes)):
                    found_list.append(extraLine_attributes[l])
                new_row = {current_header: found_list}
                row_dict.update(new_row)
            else:
                if extraLine_attributes[0] != "None":
                    success = False
                    return success, f"{extraLine_attributes[0]} is not found in list of attributes.", None

        changeDataType(row_dict)

        new_row = {attributes[0]: row_dict}
        dictionary.update(new_row)

    return success, None, dictionary

def loadDatabase(path, includeID):
    success = True
    dictionary = {}

    try:
        open(path, "r")
    except FileNotFoundError as e:
        success = False
        return success, e, None

    with open(path, "r", encoding='utf-8-sig') as database:
        header = database.readline().strip().split(",")
        lines = database.readlines()
        readSuccess, errorMessage, readDictionary = readRecord(dictionary, header, lines, includeID)
        if not readSuccess:
            return readSuccess, errorMessage, dictionary

    for i in header:
        if i[-6:] == "db.csv":
            attributeDictionary = {}

            with open(i, "r", encoding='utf-8-sig') as attributeDatabase:
                attributeHeader = attributeDatabase.readline().strip().split(",")
                attributeLines = attributeDatabase.readlines()
                csvSuccess, errorMessage, csvDictionary = readRecord(attributeDictionary, attributeHeader, attributeLines, True)
                if not csvSuccess:
                    return csvSuccess, errorMessage, None

            if type(readDictionary[list(readDictionary.keys())[0]][i]) is list:
                for record in readDictionary:
                    for listID in readDictionary[record][i]:
                       if listID != "N/A":
                            found_record = csvDictionary[listID]
                            readDictionary[record][i] = {listID : found_record}
            else:
                for record in readDictionary:
                    if readDictionary[record][i] != "N/A":
                        try:
                            csvDictionary[readDictionary[record][i]]
                        except KeyError as e:
                            return success, e, None
                        else:
                            readDictionary[record][i] = csvDictionary[readDictionary[record][i]]


    return success, None, readDictionary

def modifyRecord(dictionary, id, ignoreList):
    success = True
    try:
        dictionary[id]
    except KeyError as e:
        success = False
        return success, e

    current_row = dictionary[id]
    print("Enter '/' to return.")

    def enter_new(key):
        data = current_row[key]
        data_type = type(data)
        if data_type is int:
            new_input = input(f"Enter new \033[1m{key.lower().strip("@")}\033[0m (Value: integer): ").strip()
            if new_input == "/":
                return False
            try:
                int(new_input)
            except ValueError:
                print('\033[31m!! Warning: please enter the correct data type. Current data type is an integer. !!\033[0m')
                enter_new(key)
                return
        elif data_type is list:
            new_input = []
            stop = False
            length = len(data)
            while stop == False:

                list_input = input(f"Enter new values for \033[1m{key.lower().strip("@")}\033[0m (Type  '/'  to finish entering values): ").strip()
                if not key.strip("@") == key:
                    try:
                        int(list_input)
                    except ValueError:
                        pass
                    else:
                        list_input = int(list_input)

                if list_input != "/":
                    new_input.append(list_input)
                else:
                    stop = True

                if len(new_input) == len(length):
                    stop = True
        elif data_type is dict:
            print("Enter 'N/A' if data is currently unavailable.")
            new_input = input(f"Enter new \033[1m{key.lower().strip("@")}\033[0m (Value: ID of {key.split("db.csv")[0]} database): ").strip()
            if new_input == "/":
                return False
            success, errorMessage, dictionary = extra.loadDatabase(key, True)
            if success:
                try:
                    dictionary[new_input]
                except (KeyError, IndexError) as e:
                    return False
                else:
                    new_input = dictionary[new_input]
            else:
                print(f'\033[31m{errorMessage}\033[0m')
        else:
            new_input = input(f"Enter new \033[1m{key.lower().strip("@")}\033[0m: ").strip()
            if new_input == "/":
                return False

        current_row[key] = new_input
        return True

    for i in current_row:
        if ignoreList:
            if i not in ignoreList:
                success = enter_new(i)
                if not success:
                    break
        else:
            success = enter_new(i)
            if not success:
                break

    return success

def saveData(dictionary, path):
    success = True

    try:
        open(path, "r")
    except FileNotFoundError as e:
        success = False
        return success, e
    else:
        with open(path, "r", encoding='utf-8-sig') as database:
            header = database.readline().strip().split(",")

        lines = []
        lines.append(",".join(map(str, header)) + "\n")

        count = 0
        for id in dictionary:
            line = []
            extraLines = []
            line.append(id)
            for attribute_key in dictionary[id]:
                attribute_value = dictionary[id][attribute_key]
                if type(attribute_value) is list:
                    list_line = []
                    list_line.append(attribute_key)
                    for i in attribute_value:
                        list_line.append(i)
                    extraLines.append(",".join(map(str, list_line)) + "\n")

                elif type(attribute_value) is dict:
                    attribute_value = attribute_value[list(attribute_value.keys())[0]]
                    line.append(attribute_value)
                else:
                    line.append(attribute_value)


            lines.append(",".join(map(str, line)) + "\n")


            count += 1

            for extraLine in extraLines:
                lines.append(extraLine)
                count += 1

        for i in range(0, len(lines)):
            if i == len(lines)-1:
                lines[i] = lines[i].strip("\n")

        with open(path, "w", encoding='utf-8-sig') as database:
            for i in lines:
                database.write(i)

    return success, None

def checkDict(success, dictionary, key):
    success = False

    for i in dictionary:
        if dictionary[i] == key:
            success = True
        elif type(dictionary[i]) is dict:
            checkDictSuccess = checkDict(success, dictionary[i], key)
            if checkDictSuccess:
                success = True

    return success

def checkDBExistence(key):
    success = False
    errorMessage = None
    path = None
    dictID = None
    found_fileName = None

    roles = ["course", "class", "classroom", "resources"]
    for i in roles:
        file_name = i.lower()
        file_name += "db.csv"
        readSuccess, errorMessage, dictionary = extra.loadDatabase(file_name, False)
        if not readSuccess:
            return readSuccess, errorMessage, None
        else:
            for record in dictionary:
                if record == key:
                    success = True
                    path = dictionary
                    dictID = record
                    found_fileName = file_name
                    break

                attribute = dictionary[record][list(dictionary[record].keys())[0]]

                if attribute == key:
                    success = True
                    path = dictionary
                    dictID = record
                    found_fileName = file_name
                    break

    return success, errorMessage, found_fileName, path, dictID

def checkUserExistence(key):
    errorMessage = None
    path = None
    dictID = None
    roleID = None
    found_roleDictionary = None
    found_userDictionary = None
    userSuccess = False
    roleSuccess = False

    readSuccess, errorMessage, dictionary = extra.loadDatabase("userdb.csv", False)
    if not readSuccess:
        return None, None, errorMessage
    else:
        for record in dictionary:
            if record == key:
                userSuccess = True
                found_userDictionary = dictionary
                dictID = record
                break

    roles = ["admin", "teacher", "student", "staff"]
    for i in roles:
        file_name = i.lower()
        file_name += "db.csv"
        readSuccess, errorMessage, roleDictionary = extra.loadDatabase(file_name, False)
        if not readSuccess:
            return None, None, errorMessage
        else:
            for record in roleDictionary:
                if record == key:
                    roleSuccess = True
                    path = file_name
                    roleID = record
                    found_roleDictionary = roleDictionary

                if roleDictionary[record]["userdb.csv"][list(roleDictionary[record]["userdb.csv"])[0]] == key:
                    roleSuccess = True
                    path = file_name
                    roleID = record
                    found_roleDictionary = roleDictionary

    if userSuccess or roleSuccess:
        return ["userdb.csv", dictionary, dictID, userSuccess], [path, found_roleDictionary, roleID, roleSuccess], None
    else:
        return None, None, "Error in finding user/role."
    
def displayRecords(path):
    success, errorMessage, dictionary = extra.loadDatabase(path, False)
    if not success:
        print(f'\33[31m{errorMessage}\33[0m')
        teacher()
        return
    else:
        for i in dictionary:
            count = 0
            for j in dictionary[i]:
                count += 1

                words = j.split("_")
                for letter in range(0, len(words)):
                    words[letter] = words[letter].capitalize()
                new_attribute = " ".join(words)
                new_attribute = new_attribute.strip("@")
                if type(dictionary[i][j]) is list:
                    displayList(new_attribute, dictionary[i][j])
                elif type(dictionary[i][j]) is dict:
                    print(f"| {new_attribute}: {dictionary[i][j][list(dictionary[i][j].keys())[0]]}", end=' ')
                else:
                    print(f"| {new_attribute}: {dictionary[i][j]}", end=' ')
                if count == len(dictionary[i]):
                    print("|")

def findRecord(path, key):
    success = True
    dictionary = {}

    try:
        open(path, "r")
    except FileNotFoundError as e:
        success = False
        return success, e, None
    else:
        with open(path, "r", encoding='utf-8-sig') as database:
            header = database.readline().strip().split(",")
            count = 0
            lines = database.readlines()
            readRecord(dictionary, header, lines, True)

    return success, None, dictionary[key]

def displayList(attribute, givenList):
    print(f"| {attribute}: ", end=" ")
    for i in range(0, len(givenList)):
        if i == len(givenList) - 1:
            print(f"{givenList[i]}", end="")
        else:
            print(f"{givenList[i]}", end=", ")

def course_creation_management(teacher_id):
    print("\n--- Course Creation and Management ---")
    print("1 - Course Creation")
    print("2 - Course Management")
    print("3 - Class Creation")
    print("4 - Class Management")
    print("5 - Exit")

    action = input("Enter a number between the option to lead to the part you needed: ").strip()
    if action == "1":
        success, error, database = extra.loadDatabase("coursedb.csv", False)
        if success:
            print(database)
        else:
            print(f"Error: {error}")
        course_id = input("Enter course id: ").strip()
        course_name = input("Enter course name: ").strip()
        database[course_id] = {
            "course_id" : course_id,
            "course_name": course_name,
            "class_name": [],
            "scheduledb.csv": [],
            "assignments": []
        }

        success = extra.modifyRecord(database, course_id, None)
        if not success:
            course_creation_management(teacher_id)
            return

        success, error = extra.saveData(database, "coursedb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")
            
    elif action == "2":
        course_id_update = input("Enter Course id to update: ").strip()
        course_name = input("Enter Course name to update: ").strip()

        success, error, database = extra.loadDatabase("coursedb.csv", False)
        if success:
            print("Data loaded successfully.")
        else:
            print(f"Error: {error}")
            
        if course_id_update in database:
            database[course_id_update]["course_name"] = course_name
            print("Course updated successfully")
        else:
            print(f"Course '{course_id_update}' not found.")

        success, error = extra.saveData(database, "coursedb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")

    elif action == "3":
        success, error, database = extra.loadDatabase("classdb.csv", False)
        if success:
            print(database)
        else:
            print(f"Error: {error}")
        class_id = input("Enter class ID: ").strip()

        success, error, record = findRecord("classdb.csv", class_id)
        if not success:
            print(error)
            course_creation_management(teacher_id)
            return

        success, error = extra.modifyRecord(database, class_id, None)
        if not success:
            print(error)
            course_creation_management(teacher_id)
            return

        success, error = extra.saveData(database, "coursedb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")
            
    elif action == "4":
        class_ID_update = input("Enter Class ID to update: ").strip()

        success, error, database = extra.loadDatabase("classdb.csv", False)
        if not success:
            print(error)
            course_creation_management(teacher_id)
            return

        try:
            database[class_ID_update]
        except KeyError as e:
            print(f"Class '{class_ID_update}' not found.")
            course_creation_management(teacher_id)
            return

        success, error = extra.modifyRecord(database, class_ID_update, None)
        if not success:
            print(error)
            course_creation_management(teacher_id)
            return

        success, error = extra.extra.saveData(database, "coursedb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")

    elif action == "5":
        teacher(teacher_id)
        return
    else:
        print("This dosen't belong to any single code in our system")
        teacher(teacher_id)
        return

    course_creation_management(teacher_id)

def student_enrolment(teacher_id):
    print("\n--- Student Enrolment ---")
    print("1 - Enroll Student")
    print("2 - Remove Student")
    print("3 - Exit")

    action = input("Enter a number between the option to lead to the part you needed: ").strip()
    if action == "1":
        studentdatabase = displayRecords("studentdb.csv")
        student_id = input("Enter student id: ")
        success, errorMessage, record = findRecord("studentdb.csv", student_id)
        if not success:
            print(f"Error: {errorMessage}")
        else:
            print("Record found: ", record)

        success, error, teacherdatabase = extra.loadDatabase("teacherdb.csv", False)
        success, errorMessage, record = findRecord("teacherdb.csv", teacher_id)

        if student_id in studentdatabase:
            studentdatabase[student_id]["coursedb.csv"]["course_id"] = teacherdatabase[teacher_id]["coursedb.csv"]["course_id"]
            success, error = extra.saveData(studentdatabase, "studentdb.csv")
            if not success:
                print(error)


    elif action == "2":
        success,error, studentdatabase = extra.loadDatabase("studentdb.csv", False)
        success,error, teacherdatabase = extra.loadDatabase("teacherdb.csv", False)

        student_id = input("Enter student ID: ").strip()

        if studentdatabase[student_id] != None:
            if studentdatabase[student_id]["coursedb.csv"]["course_id"] == teacherdatabase[teacher_id]["coursedb.csv"]["course_id"]:
                del database[student_id]
                print("Student removed successfully.")
            else:
                print(f"Student '{studentdatabase[student_id]["student_name"]}' does not belong to your course.")
        else:
            print(f"Student '{studentdatabase[student_id]["student_name"]}' not found in course '{teacherdatabase[teacher_id]["coursedb.csv"]["course_name"]}")

        success, error = extra.saveData(studentdatabase, "studentdb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")

    elif action == "3":
        teacher(teacher_id)
        return
    else:
        print("This dosen't belong to any single code in our system")
        teacher(teacher_id)
        return

    student_enrolment(teacher_id)

def grading_assessment(teacher_id):
    """Grading and Assessment function for handling assignments and exams"""
    print("\n--- Grading and Assessment ---")
    print("1 - Assignments")
    print("2 - Exam ")
    print("3 - Type in student semester gpa")
    print("4 - Exit")

    action = input("Enter a number to choose the part you need: ").strip()

    success, error, database = extra.loadDatabase("gradingdb.csv", False)

    if action == "1":
        gradingID = input("Enter grading ID: ").strip()
        studentID = input("Enter student ID: ").strip()
        StudentName = input("Enter student name: ").strip()
        classID = input("Enter class ID: ").strip()
        className = input("Enter class name: ").strip()

        assignment_marks = getValidInput("Enter assignment marks (0-100): ", 0, 100)

        assignment_gpa = markToGpa(assignment_marks)

        feedback = input("Enter feedback: ").strip()

        database[gradingID] = {
            "studentdb.csv": {"student_id": studentID,
                              "student_name": StudentName},
            "classdb.csv": {"class_id" :classID,
                            "class_name": className},
            "exam_marks": "N/A",
            "exams_gpa@": "N/A",
            "assignment_marks": assignment_marks,
            "assignment_gpa@": assignment_gpa,
            "feedback": feedback
        }

        success, error = extra.saveData(database, "gradingdb.csv")
        if success:
            print("Assignment grading data saved successfully.")
        else:
            print(f"Error: {error}")

    elif action == "2":
        gradingID = input("Enter grading ID: ").strip()
        studentID = input("Enter student ID: ").strip()
        StudentName = input("Enter student name: ").strip()
        classID = input("Enter class ID: ").strip()
        className = input("Enter class name: ").strip()

        exam_marks = getValidInput("Enter exam marks (0-100): ", 0, 100)

        exam_gpa = markToGpa(exam_marks)

        feedback = input("Enter feedback: ").strip()

        database[gradingID] = {
            "studentdb.csv": {"student_id": studentID,
                              "student_name": StudentName},
            "classdb.csv": {"class_id": classID,
                             "class_name": className},
            "exam_marks": exam_marks,
            "exams_gpa@": exam_gpa,
            "assignment_marks": "N/A",
            "assignment_gpa@": "N/A",
            "feedback": feedback
        }

        success, error = extra.saveData(database, "gradingdb.csv")
        if success:
            print("Exam result recorded successfully.")
        else:
            print(f"Error: {error}")

    elif action == "3":
        student_id = input("Enter student id: ")
        success, errorMessage, record = findRecord("studentdb.csv", student_id)
        if not success:
            print(f"Error: {errorMessage}")
            grading_assessment(teacher_id)
            return

        success, error, studentdatabase = extra.loadDatabase("studentdb.csv", False)
        print("Record found: ", record)

        ignoreList = ["student_id","student_name","@student_contact","coursedb.csv","enrolment_status","academic_performance","emergency_contact_name","@emergency_contact","relationship_to_student","fees_outstanding","fees_paid","next_payment_date","userdb.csv"]
        success = extra.modifyRecord(studentdatabase, student_id, ignoreList)
        if not success:
            print(f"Error: {error}")
            grading_assessment(teacher_id)
            return

        success, error = extra.saveData(database, "gradingdb.csv")
        if success:
            print("Student gpa recorded.")
        else:
            print(f"Error: {error}")

    elif action == "4":
        teacher(teacher_id)
        return

    else:
        print("This doesn't belong to any single code in our system")
        return

    grading_assessment(teacher_id)

def attendance_tracking(teacher_id):
    print("\n--- Attendance Tracking ---")
    print("1 - Record")
    print("2 - Enter Event")
    print("3 - Exit")

    action = input("Enter a number between the option to lead to the part you needed: ").strip()

    if action == "1":
        success, error, database = extra.loadDatabase("attendance_trackingdb.csv", False)
        if not success:
            print(error)
            attendance_tracking(teacher_id)
            return

        attendance_id = input("Enter attendance ID: ").strip()
        student_id = input("Enter student ID: ").strip()
        student_name = input("Enter student name: ").strip()
        class_id = input("Enter class ID: ").strip()
        class_name = input("Enter class name: ").strip()
        date = input("Enter date: ").strip()
        status = input("Enter status(Present/Absent): ").strip()

        database[attendance_id] = {
            "studentdb.csv": {"student_id": student_id,
                              "student_name": student_name},
            "classdb.csv": {"class_id": class_id,
                            "class_name": class_name},
            "eventsdb.csv": "N/A",
            "date": date,
            "status": status
        }

        success, error = extra.saveData(database, "attendance_trackingdb.csv")
        if success:
            print("Attendance tracking successfully.")
        else:
            print(f"Error: {error}")

    elif action == "2":
        success, error, database = extra.loadDatabase("attendance_trackingdb.csv", False)
        if not success:
            print(error)
            attendance_tracking(teacher_id)
            return

        attendance_id = input("Enter attendance ID: ").strip()
        student_id = input("Enter student ID: ").strip()
        student_name = input("Enter student name: ").strip()
        event_id = input("Enter event ID: ").strip()
        event_name = input("Enter event name: ").strip()
        date = input("Enter date: ").strip()
        status = input("Enter status(Present/Absent): ").strip()

        database[attendance_id] = {
            "studentdb.csv": {"student_id": student_id,
                              "student_name": student_name},
            "classdb.csv": "N/A",
            "eventsdb.csv": {"EventID": event_id,
                             "EventName": event_name},
            "date": date,
            "status": status
        }

        success, error = extra.saveData(database, "attendance_trackingdb.csv")
        if success:
            print("Data saved successfully.")
        else:
            print(f"Error: {error}")

    elif action == "3":
        teacher(teacher_id)
        return
    else:
        print("This dosen't belong to any single code in our system")
        teacher(teacher_id)
        return

    attendance_tracking(teacher_id)

def report_generation(teacher_id):
    print("\n--- Report Generation ---")
    print("1 - Performance ")
    print("2 - Participation")
    print("3 - Exit")

    action = input("Enter a number between the option to lead to the part you needed: ").strip()

    if action == "1":
        success, error, database = extra.loadDatabase("studentdb.csv", False)

        for i in database:
            print(f"| {i} | Student Name: {database[i]["student_name"]} | Academic Performance: {database[i]["academic_performance"]} |")

    elif action == "2":
        displayRecords("attendance_trackingdb.csv")

    elif action == "3":
        teacher(teacher_id)
        return
    else:
        print("This dosen't belong to any single code in our system")
        teacher(teacher_id)
        return

    report_generation(teacher_id)
    
def logout():
    print("Thank you for using our systems! ")
    import mainmenu
    mainmenu.hompage()

def teacher(teacher_id):
    print("\n--- Main Menu ---")
    print("1 - Course Creation and Management")
    print("2 - Student Enrolment")
    print("3 - Grading and Assessment")
    print("4 - Attendance Tracking")
    print("5 - Report generation ")
    print("6 - Logout")

    action = input("Enter a number between the option to lead to the part you needed: ")

    if action == "1":
        course_creation_management(teacher_id)
        teacher(teacher_id)
        return
    if action == "2":
        student_enrolment(teacher_id)
        teacher(teacher_id)
        return
    if action == "3":
        grading_assessment(teacher_id)
        teacher(teacher_id)
        return
    if action == "4":
        attendance_tracking(teacher_id)
        teacher(teacher_id)
        return
    if action == "5":
        report_generation(teacher_id)
        teacher(teacher_id)
        return

    if action == "6":
        logout()
        teacher(teacher_id)
        return
    
    else:
        print("This dosen't belong to any single code in our system")
        teacher(teacher_id)

teacher("LT0001")