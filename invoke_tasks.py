"""
Brothers Baking Data Pipeline - Invoke Tasks
Main task orchestration file for the Brothers Baking analytics pipeline

Usage:
    invoke --list                    # List all available tasks
    invoke pipeline.all              # Run complete pipeline
    invoke pipeline.status           # Check pipeline status
    invoke app.run                   # Start the dashboard
    invoke extract.all               # Run all extraction tasks
    invoke format.all                # Run all formatting tasks
    invoke combine.all               # Run all combination tasks
"""

from invoke import Collection
import task_modules.extract as extract
import task_modules.format as format
import task_modules.combine as combine
import task_modules.pipeline as pipeline
import task_modules.app as app

# Create the main task collection
ns = Collection()

# Add task modules as sub-collections
ns.add_collection(extract, name='extract')
ns.add_collection(format, name='format') 
ns.add_collection(combine, name='combine')
ns.add_collection(pipeline, name='pipeline')
ns.add_collection(app, name='app')

# Add some top-level convenience tasks
ns.add_task(pipeline.all, name='run-pipeline')
ns.add_task(pipeline.status, name='status')
ns.add_task(app.run, name='run-app')
ns.add_task(app.check_data, name='check-data') 