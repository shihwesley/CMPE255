import apache_beam as beam


class CustomTransform(beam.PTransform):

    def expand(self, input_coll):

        a = (input_coll | 'Group and sum' >> beam.CombinePerKey(sum) |
             'count filter accounts' >> beam.Filter(filter_on_count) |
             'Regular accounts employee' >> beam.Map(format_output))
        return a


def SplitRow(element):
    return element.split(',')


def filter_on_count(element):
    name, count = element
    if count > 0:
        return element


def format_output(element):
    name, count = element
    #return ', '.join((name.encode('ascii'),str(count),'Regular employee'))
    return ', '.join((name, str(count), 'Regular Patient'))


p = beam.Pipeline()

input_collection = (
    p | "Read from text file" >> beam.io.ReadFromText('dept_data.txt') |
    "Split rows" >> beam.Map(SplitRow))

cardio_count = (
    input_collection | 'Get all cardio patients' >>
    beam.Filter(lambda record: record[3] == 'cardio') |
    'Pair each patient with 1' >>
    beam.Map(lambda record: ("cardio, " + record[1], 1)) | CustomTransform() |
    'Write results for cardio' >> beam.io.WriteToText('cardio_output.txt'))

ortho_count = (
    input_collection | 'Get all HR dept persons' >>
    beam.Filter(lambda record: record[3] == 'ortho') |
    'Pair each hr employee with 1' >> beam.Map(lambda record:
                                               ("ortho, " + record[1], 1)) |
    'composite Ortho Patients' >> CustomTransform() |
    'Write results for Ortho' >> beam.io.WriteToText('ortho_output.txt'))

p.run()
