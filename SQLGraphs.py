import tkinter as tk
import numpy as np
import pandas as pd
import sqlite3


from tkinter import filedialog
from tkinter import ttk
from tkinter import *


class App:
    def __init__(self):

        self.x_position = 10
        self.widgets_dict = {}

        self.db_path = ""
        self.db_tables = []
        
        self.selected_cols = {}
        self.selected_aggregations = {}

        self.dict_of_canvases = {}
        self.aggregations_cols_select_dict = {}

        self.root = tk.Tk()
        

        self.root.geometry("800x380")

        self.cTableContainer = tk.Canvas(self.root)
        self.sbHorizontalScrollBar = tk.Scrollbar(self.root)
        self.sbVerticalScrollBar = tk.Scrollbar(self.root)

        self.frame = tk.Frame(self.cTableContainer)
        self.frame.grid(sticky = "nsew")


        self.importLabel = tk.Label(self.frame, text = 'Import database:', font = ('Arial', 12))
        self.importLabel.grid(row=1, column = 1, padx = 10, pady = 10, sticky = 'w')

        self.getDB_btn = tk.Button(self.frame, text = 'Select database', font = ('Arial', 12), command= self.getDB)
        self.getDB_btn.grid(row=1, column=1, padx = 150, pady = 10, sticky='w')


        self.createScrollableContainer()
        self.root.mainloop()


    def getDB(self):
        
        self.db_path = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("All files","*.*"),("Databases", "*.db*")))

        self.getTables(self.db_path)

    def getTables(self, db_path):
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        self.tables = self.cursor.fetchall()
        for table_name in self.tables:
            self.db_tables.append(table_name[0])
        self.cursor.close()
        self.conn.close()

        self.selectTable()


    def selectTable(self):
        self.table_select_Label = tk.Label(self.frame, text = 'Select table:', font = ('Arial',12))
        self.table_select_Label.grid(row=2, column=1, padx = 10, pady = 10, sticky='w') 

        self.table_select = ttk.Combobox(self.frame, width = 20)
        self.table_select['values'] = self.db_tables
        self.table_select.grid(row=2, column=1, padx=110, pady = 10, sticky='w')
        self.table_select.bind('<<ComboboxSelected>>', self.add_func_button)


    def add_func_button(self, event):
        self.add_btn = tk.Button(self.frame, text = 'Add function', font = ('Arial', 12))
        self.add_btn.grid(row = 3, column = 1, padx = 10, pady = 10, sticky='w')
        self.add_btn.bind('<Button-1>', self.selectFunc)


    def selectFunc(self, event):
        
        event.widget.grid(row = event.widget.grid_info().get('row') + 1, column = 1, padx = 10, pady = 10, sticky = 'w')

        self.add_func = ttk.Combobox(self.frame, width = 20)
        self.add_func['values'] = ['SELECT', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
                                   'LIKE', 'AND', 'OR', 'BETWEEN', 'CAST', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN',
                                   'FULL JOIN']
        
        
        if len(self.widgets_dict) == 0:
            self.add_func.grid(row = 3, column= 1, padx = 10, pady= 10, sticky='w')
        else:            
            self.add_func.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column=1, padx = 10, pady = 10, sticky='w')

        
        self.updateScrollRegion()
        self.add_func.bind('<<ComboboxSelected>>', self.do_further)

        
  

    def do_further(self, event):
        
        #If widget was previously selected, remove all instances related to it
        if event.widget in self.widgets_dict: 
            for i in self.widgets_dict.get(event.widget):
                try:
                    i.grid_forget()
                except:
                    pass
            
            self.widgets_dict.pop(event.widget, None)
            
            
            
        if event.widget.get() == 'SELECT':
            
            self.select_chosen(event) 


        elif event.widget.get() == 'WHERE':
            
            self.where_chosen(event)

        elif event.widget.get() == 'GROUP BY':

            self.groupBy_chosen(event)

        elif event.widget.get(event) == 'HAVING':

            self.having_chosen(event)

        elif event.widget.get() == 'ORDER BY':
            
            self.orderBy_chosen(event)

        elif event.widget.get() == 'SUM':

            self.sum_chosen(event)

        elif event.widget.get() == 'COUNT':

            self.count_chosen(event)

        elif event.widget.get() == 'COUNT (distinct)':

            self.countDistinct_chosen(event)

        elif event.widget.get() == 'AVG':

            self.avg_chosen(event)

        elif event.widget.get() == 'MIN':

            self.min_chosen(event)

        elif event.widget.get() == 'MAX':

            self.max_chosen(event)

        elif event.widget.get() == 'LIKE':

            self.like_chosen(event)

        elif event.widget.get() == 'AND':

            self.and_chosen(event)

        elif event.widget.get() == 'OR':

            self.or_chosen(event)

        elif event.widget.get() == 'BETWEEN':

            self.between_chosen(event)

        elif event.widget.get() == 'CAST':
            
            self.cast_chosen(event)

        elif event.widget.get() == 'INNER JOIN':

            self.innerJoin_chosen(event)

        elif event.widget.get() == 'LEFT JOIN':

            self.leftJoin_chosen(event)

        elif event.widget.get() == 'RIGHT JOIN':

            self.rightJoin_chosen(event)

        elif event.widget.get() == 'FULL JOIN':

            self.fullJoin_chosen(event)


        else:
            pass


    
    def add_cols_func(self, event):

        event.widget.grid(row = event.widget.grid_info().get('row') + 1, column = 1, padx = 10, pady = 10, sticky = 'w')
        

        if len(self.aggregations_cols_select_dict) == 0:
            
            self.agg_functions_selection = ttk.Combobox(event.widget.master, width= 10)
            self.agg_functions_selection['values'] = ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX']
            self.agg_functions_selection.grid(row = 1, column=1, pady = 10, sticky='w')

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            

            self.cols_selection = ttk.Combobox(event.widget.master, width = 10)
            self.cols_selection['values'] = ['*'] + [columns[0] for columns in self.col_names]
            self.cols_selection.grid(row = 1, column=2, pady = 10, sticky='w')

            self.aggregations_cols_select_dict[event.widget.master] = [self.agg_functions_selection, self.cols_selection]
        
        else:
            

            self.agg_functions_selection = ttk.Combobox(event.widget.master, width= 10)
            self.agg_functions_selection['values'] = ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX']
            self.agg_functions_selection.grid(row = self.aggregations_cols_select_dict.get(event.widget.master)[0].grid_info().get('row') + 1, column=1, pady = 10, sticky='w')

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            

            self.cols_selection = ttk.Combobox(event.widget.master, width = 10)
            self.cols_selection['values'] = ['*'] + [columns[0] for columns in self.col_names]
            self.cols_selection.grid(row = self.aggregations_cols_select_dict.get(event.widget.master)[1].grid_info().get('row') + 1, column=2, pady = 10, sticky='w')

            self.aggregations_cols_select_dict[event.widget.master] = [self.agg_functions_selection, self.cols_selection]


    
    def select_chosen(self, event):
        if len(self.widgets_dict) == 0:
            
            

            self.container = tk.Frame(self.frame)
            self.container.grid(row = 3, column=2, padx= 10, pady= 10, sticky='nsew')
            
            self.canvas = tk.Canvas(self.container)
            self.scrollbar = ttk.Scrollbar(self.container, orient='vertical', command = self.canvas.yview)

            self.canvas.grid(row = 1, column=1, sticky='nsew')
            self.scrollbar.grid(row=1, column =2, sticky="ns")

            self.scrollable_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw')
            
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            self.add_cols_btn = tk.Button(self.scrollable_frame, text = 'Add Columns', font = ('Arial', 12))
            self.add_cols_btn.bind('<Button-1>',self.add_cols_func)
            self.add_cols_btn.grid(row = 1, column=1, sticky='w')

            self.dict_of_canvases[self.scrollable_frame] = self.add_cols_btn
        
        else:

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()
            

            #Creating canvas where user selects columns to analyze
            self.container = tk.Frame(self.frame)
            self.container.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column=1, padx= event.widget.winfo_rootx()+150, pady= 10, sticky='nsew')
            
            self.canvas = tk.Canvas(self.container)
            self.scrollbar = ttk.Scrollbar(self.container, orient='vertical', command = self.canvas.yview)

            self.canvas.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column=0, sticky='nsew')
            self.scrollbar.grid(row=list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column =0, sticky="ns")

            self.scrollable_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw')
            
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            

            self.add_cols_btn = tk.Button(self.scrollable_frame, text = 'Add Columns', font = ('Arial', 12))
            self.add_cols_btn.bind('<Button-1>',self.add_cols_func)
            self.add_cols_btn.grid(row = 1, column=1, sticky='w')

            self.dict_of_canvases[self.scrollable_frame] = self.add_cols_btn

            
            


    def where_chosen(self, event):


        if len(self.widgets_dict) == 0:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            self.col_names_list = [col[0] for col in self.col_names]

            self.where_col_select = ttk.Combobox(self.frame, width = 10)
            self.where_col_select['values'] = self.col_names_list
            self.where_col_select.grid(row=3, column=1, padx=event.widget.winfo_rootx() + 150, pady = 10, sticky='w')
            
            
            self.comparison = ttk.Combobox(self.frame, width = 10)
            self.comparison['values'] = ['=', '>', '<', '>=', '<=', 'Not =', 'Not >', 'Not <']
            self.comparison.grid(row = 3, column = 1, padx = self.where_col_select.winfo_rootx() + 270, pady = 10, sticky='w')
            
            

            self.col_value = tk.Text(self.frame, width = 10, height = 1)
            self.col_value.grid(row = 3, column = 1, padx = self.comparison.winfo_rootx() + 370, pady= 10, sticky='e')
            
            
            self.widgets_dict[event.widget] = (event.widget.get(), self.where_col_select, self.comparison, self.col_value)

        else:
            
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            self.col_names_list = [col[0] for col in self.col_names]

            self.where_col_select = ttk.Combobox(self.frame, width = 10)
            self.where_col_select['values'] = self.col_names_list
            self.where_col_select.grid(row=list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column=1, padx=1, pady = 10, sticky='e')
            
            
            self.comparison = ttk.Combobox(self.frame, width = 10)
            self.comparison['values'] = ['=', '>', '<', '>=', '<=', 'Not =', 'Not >', 'Not <']
            self.comparison.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column = 2, padx = 1, pady = 10, sticky='e')
            
            

            self.col_value = tk.Text(self.frame, width = 10, height = 1)
            self.col_value.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column = 3, padx = 1, pady= 10, sticky='e')
            
            
            self.widgets_dict[event.widget] = (event.widget.get(), self.where_col_select, self.comparison, self.col_value)

    def groupBy_chosen(self, event):
        if len(self.widgets_dict) == 0:

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            self.col_names_list = [col[0] for col in self.col_names]

            self.groupBy_col_select = ttk.Combobox(self.frame,width = 10)
            self.groupBy_col_select['values'] = self.col_names_list
            self.groupBy_col_select.grid(row = 3, column = 2, padx=2, pady = 1, sticky='w')

            self.widgets_dict[event.widget] = (event.widget.get(), self.groupBy_col_select)

        else:

            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT c.name FROM pragma_table_info('{self.table_select.get()}') c;")
            self.col_names = self.cursor.fetchall()
            
            self.cursor.close()
            self.conn.close()

            self.col_names_list = [col[0] for col in self.col_names]

            self.groupBy_col_select = ttk.Combobox(self.frame,width = 10)
            self.groupBy_col_select['values'] = self.col_names_list
            self.groupBy_col_select.grid(row = list(self.widgets_dict.keys())[-1].grid_info().get('row')+1, column = 2, padx=1, pady = 10, sticky='w')

            self.widgets_dict[event.widget] = (event.widget.get(), self.groupBy_col_select)



    def having_chosen(self, event):
        print('Having')

    def orderBy_chosen(self, event):
        print('Order BY')

    def sum_chosen(self, event):
        print('Sum')

    def count_chosen(self,event):
        print('COunt')

    def countDistinct_chosen(self, event):
        print('Count dist')

    def avg_chosen(self, event):
        print('Avg')

    def min_chosen(self, event):
        print('Min')

    def max_chosen(self, event):
        print('Max')

    def like_chosen(self, event):
        print('Like')

    def and_chosen(self, event):
        print('and')

    def or_chosen(self, event):
        print('or')

    def between_chosen(self,event):
        print('Between')

    def cast_chosen(self, event):
        print('cast')

    def innerJoin_chosen(self, event):
        print('Inner')

    def leftJoin_chosen(self,event):
        print('Left')

    def rightJoin_chosen(self, event):
        print('Right')

    def fullJoin_chosen(self, event):
        print('Full')


    def updateScrollRegion(self):
        self.cTableContainer.update_idletasks()
        self.cTableContainer.config(scrollregion=self.frame.bbox())

    # Sets up the Canvas, Frame, and scrollbars for scrolling
    def createScrollableContainer(self):
        self.cTableContainer.config(xscrollcommand=self.sbHorizontalScrollBar.set,yscrollcommand=self.sbVerticalScrollBar.set, highlightthickness=0)
        self.sbHorizontalScrollBar.config(orient=tk.HORIZONTAL, command=self.cTableContainer.xview)
        self.sbVerticalScrollBar.config(orient=tk.VERTICAL, command=self.cTableContainer.yview)

        self.sbHorizontalScrollBar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
        self.sbVerticalScrollBar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.cTableContainer.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)
        self.cTableContainer.create_window(0, 0, window=self.frame, anchor=tk.NW)

if __name__ == "__main__":
    App()