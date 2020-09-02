"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import datetime
from aiohttp import web


def convert_average_time(records):
    result = []
    for row in records:
        item = dict(row.items())
        item['avg_time'] = str(datetime.timedelta(seconds=int(item['avg_time'].seconds))) if item['avg_time'] else 0
        result.append(item)
    return result


async def show_searches(request):
    async with request.app['engine'].acquire() as conn:
        all_searches = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE description !='sequence-search-test' OR description IS NULL"
        )
        all_searches_records = await all_searches.fetchall()
        all_searches_result = convert_average_time(all_searches_records)
        all_searches_result[0].update({'search': 'all'})

        last_24_hours = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) AND submitted > %s",
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
        last_24_hours_records = await last_24_hours.fetchall()
        last_24_hours_result = convert_average_time(last_24_hours_records)
        last_24_hours_result[0].update({'search': 'last-24-hours'})

        last_week = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) AND submitted > %s",
            datetime.datetime.now() - datetime.timedelta(days=7)
        )
        last_week_records = await last_week.fetchall()
        last_week_result = convert_average_time(last_week_records)
        last_week_result[0].update({'search': 'last-week'})

        searches_per_month = await conn.execute(
            "SELECT date_trunc('month', submitted) AS submitted_month, count(id) FROM jobs "
            "WHERE (description !='sequence-search-test' OR description IS NULL) "
            "GROUP BY submitted_month "
            "ORDER BY submitted_month",
        )
        search_results_per_month = await searches_per_month.fetchall()
        searches_per_month_list = []
        for row in search_results_per_month:
            row_as_dict = dict(row)
            period = str(row_as_dict['submitted_month'].strftime("%Y-%m"))
            if period == "2020-05":
                # Remove 525 searches due to a bug in the batch search
                searches_per_month_list.append({period: row_as_dict['count'] - 525})
            elif period == "2020-06":
                # Add 50 searches that were performed in the test environment
                searches_per_month_list.append({period: row_as_dict['count'] + 50})
            else:
                searches_per_month_list.append({period: row_as_dict['count']})

        return web.json_response(
            all_searches_result + last_24_hours_result + last_week_result + [searches_per_month_list]
        )
