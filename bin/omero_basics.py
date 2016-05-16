import ConfigParser
from omero.gateway import BlitzGateway
from omero.sys import ParametersI
from csv import writer, QUOTE_NONE
import sys

class OMEROConnectionManager:
    """ Basic management of an OMERO Connection. Methods which make use of
        a connection will attempt to connect if connect was not already
        successfuly executed """

    def __init__(self, config_file="omero.cfg"):

        # Read the credentials file
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        self.HOST = config.get("OMEROCredentials", "host")
        self.PORT = config.getint("OMEROCredentials", "port")
        self.USERNAME = config.get("OMEROCredentials", "username")
        self.PASSWORD = config.get("OMEROCredentials", "password")

        # Set the connection as not established
        self.conn = None

    def connect(self):
        """ Create an OMERO Connection """

        # If connection already established just return it
        if self.conn is not None:
            return self.conn

        # Initialize the connection
        self.conn = BlitzGateway(self.USERNAME,
                                 self.PASSWORD,
                                 host=self.HOST,
                                 port=self.PORT)

        # Connect
        connected = self.conn.connect()

        # Check that the connection was established
        if not connected:
            sys.stderr.write("Error: Connection not available, "
                "please check your user name and password.\n")
            sys.exit(1)
        return self.conn

    def disconnect(self):
        """ Terminate the OMERO Connection """
        self.conn._closeSession()
        self.conn = None

    def hql_query(self, query, params=None):
        """ Execute the given HQL query and return the results. Optionally
            accepts a parameters object.
            For conveniance, will unwrap the OMERO types """

        # Connect if not already connected
        if self.conn is None:
            self.connect()

        if params is None:
            params = ParametersI()

        # Set OMERO Group to -1 to query across all available data
        self.conn.SERVICE_OPTS.setOmeroGroup(-1)

        # Get the Query Service
        qs = self.conn.getQueryService()

        # Execute the query
        rows = qs.projection(query, params, self.conn.SERVICE_OPTS)

        # Unwrap the query results
        unwrapped_rows = []
        for row in rows:
            unwrapped_row=[]
            for column in row:
                if column is None:
                    unwrapped_row.append(None)
                else:
                    unwrapped_row.append(column.val)
            unwrapped_rows.append(unwrapped_row)

        return unwrapped_rows

def write_csv(rows, filename, header=None):
    """ Write a CSV File with the given header and rows """

    # If there is a header to be written, ensure that it is the same length
    # as the first row.
    if header is not None and len(rows) > 0 and len(rows[0]) != len(header):
        raise ValueError("Header does not have the same number of columns "
                         "as the rows")

    # Write the CSV File
    with open(filename, 'wb') as csvfile:
        row_writer = writer(csvfile, quoting=QUOTE_NONE)
        if header is not None:
            row_writer.writerow(header)
        row_writer.writerows(rows)

def well_from_row_col(row, column):
    """ Return a meaningful Well from a well row and column. E.g.
        Row=4, Column=3 will result in a Well of D2 """

    # Convert row to character, Making use of ASCII character set numbering,
    # where A-Z is 65-90. Also increment column as it is indexed from zero
    # in the database, but not in the Well designation
    return '%s%i' %(chr(65+int(row)), column+1)
