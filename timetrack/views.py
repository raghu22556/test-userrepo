import psycopg
from psycopg import sql
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .authenticate import authenticate_request
from datetime import datetime, timedelta

@csrf_exempt
def insert_time_data(request):
    if request.method == 'POST':
        # Parse the incoming JSON data
        data = json.loads(request.body)
        # token=json.loads(request.header).token
        # token = request.headers.get("Authorization")
        # if authenticate_request(token)=='Invalid token' or authenticate_request(token)=='Token has expired': 
        #     return  JsonResponse({'status': 'error', 'message': 'Invalid login'})

        
        # Extract the resource from the input data
        resource = data.get('resource', '')  # Get the resource name
        
        # Extract the projects array containing time entries
        projects = data.get('projects', [])
        
        # Ensure the projects data is valid (not empty)
        if not projects:
            return JsonResponse({'status': 'error', 'message': 'No project data provided.'})

        # Connect to PostgreSQL database
        try:
            conn = psycopg.connect(
                dbname='users',  # Your database name
                user='postgres',  # Your PostgreSQL user
                password='Aspyr12345!',  # Your PostgreSQL password
                host='localhost',  # Your PostgreSQL host
                port='5432'  # Your PostgreSQL port
            )
            cursor = conn.cursor()

            # Loop through each project and insert the corresponding time entry
            for entry in projects:
                customer = entry['customer']
                project_name = entry['project_name']
                date = entry['date']
                hours = entry['hours']
                role = entry['role']

                # Insert data into the table
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO op_time_timetrack (tmt_resource, tmt_date, tmt_hours, tmt_customers, tmt_project, tmt_resource_role)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tmt_resource, tmt_date, tmt_project)
                        DO UPDATE SET tmt_hours = EXCLUDED.tmt_hours,
                        tmt_resource_role = COALESCE(EXCLUDED.tmt_resource_role)
                    """),
                    [resource, date, hours, customer, project_name, role]
                )

            # Commit the transaction
            conn.commit()



            # Close the cursor and connection
            cursor.close()
            conn.close()

            # Return a success response
            return JsonResponse({'status': 'success', 'message': 'Data inserted successfully.'})

        except Exception as e:
            # Handle database connection errors or query errors
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        # Return error if the request method is not POST
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method. Only POST is allowed.'})
    
@csrf_exempt
def track_hours(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON input.'})

        # Extract input parameters
        resource = data.get('resource', '').strip()
        start_date_str = data.get('start_date', '').strip()
        end_date_str = data.get('end_date', '').strip()

        if not resource or not start_date_str or not end_date_str:
            return JsonResponse({
                'status': 'error',
                'message': 'Resource, start date, and end date are required.'
            })

        try:
            # Parse the start and end dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            week_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                          for i in range((end_date - start_date).days + 1)]

            # Connect to the database
            conn = psycopg.connect(
                dbname='users',
                user='postgres',
                password='Aspyr12345!',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            # Query to fetch customer, project, date, and hours for the resource and date range
            query = """
                SELECT tmt_customers, tmt_project, tmt_date, COALESCE(tmt_hours, 0), COALESCE(tmt_resource_role, '') AS tmt_resource_role
                FROM op_time_timetrack
                WHERE tmt_resource = %s AND tmt_date BETWEEN %s AND %s
                ORDER BY tmt_customers, tmt_project, tmt_date;
            """
            cursor.execute(query, [resource, start_date_str, end_date_str])

            # Fetch query results
            results = cursor.fetchall()

            # Debug Step: Print raw query results
            print("Query Results:", results)

            # Initialize a dictionary to group data by customer and project
            customer_project_data = {}

            for customer, project, date, hours, role in results:
                key = (customer, project, role)
                formatted_date = date.strftime('%Y-%m-%d')  # Ensure date format matches week_dates
                if key not in customer_project_data:
                    customer_project_data[key] = {}
                customer_project_data[key][formatted_date] = hours

            # Debug Step: Print the grouped data
            print("Grouped Data:", customer_project_data)

            # Prepare the response data
            response_data = []
            for (customer, project, role), date_hours in customer_project_data.items():
                weekly_hours = [date_hours.get(date, 0) for date in week_dates]  # Fill missing days with 0
                response_data.append({
                    'customer': customer,
                    'project': project,
                    'role': role,
                    'weekly_hours': weekly_hours
                })

            # Debug Step: Print the response data
            print("Response Data:", response_data)

            # Close the cursor and connection
            cursor.close()
            conn.close()

            return JsonResponse({'status': 'success', 'data': response_data})

        except Exception as e:
            # Debug Step: Print exception details
            print("Error:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid HTTP method. Only POST is allowed.'
        })


@csrf_exempt
def get_customer_names(request):
    if request.method == 'GET':
        try:
            # Connect to PostgreSQL database
            conn = psycopg.connect(
                dbname='users',  # Your database name
                user='postgres',  # Your PostgreSQL user
                password='Aspyr12345!',  # Your PostgreSQL password
                host='localhost',  # Your PostgreSQL host
                port='5432'  # Your PostgreSQL port
            )
            cursor = conn.cursor()

            # Query to fetch all customer names
            cursor.execute(
                sql.SQL("SELECT DISTINCT company_name FROM customers")
            )

            # Fetch all results
            customers = cursor.fetchall()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            # Convert fetched tuples into a list of strings
            customer_names = [row[0] for row in customers]

            print(customer_names)

            # Return the list as a JSON response
            return JsonResponse({'status': 'success', 'customer_names': customer_names})

        except Exception as e:
            # Handle database connection errors or query errors
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        # Return error if the request method is not GET
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method. Only GET is allowed.'})
    


@csrf_exempt
def get_projects_by_company(request):
    if request.method == 'GET':
        # Get the company name from the query parameters
        company_name = request.GET.get('company_name', '')
        if not company_name:
            return JsonResponse({'status': 'error', 'message': 'Company name is required.'})
        
        try:
            # Connect to PostgreSQL database
            conn = psycopg.connect(
                dbname='users',  # Your database name
                user='postgres',  # Your PostgreSQL user
                password='Aspyr12345!',  # Your PostgreSQL password
                host='localhost',  # Your PostgreSQL host
                port='5432'  # Your PostgreSQL port
            )
            cursor = conn.cursor()

            # Fetch distinct projects for the given company name
            query = """
                SELECT DISTINCT project FROM customers WHERE company_name = %s;
            """
            cursor.execute(query, [company_name])
            projects = [row[0] for row in cursor.fetchall()]  # Fetch all results

            # Close the connection
            cursor.close()
            conn.close()

            return JsonResponse({'status': 'success', 'projects': projects})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method.'})
