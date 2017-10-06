using System;
using System.Collections.Generic;
using System.Linq;
using INCR;
using MVA;
using ExcelReporter;

namespace Main
{
    public static class MainClass
    {
        static void Main(string[] args)
        {
            // var shetStats = new SHET.SHET().RunSHET(10);
            // Console.WriteLine("Done...");
            // Console.WriteLine("Writing excel report...");
            // // ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("SHEt4", shetStats);
            // Console.WriteLine("Done");

            // var mvaStats = new MVAMain().RunMVA(10);
            // Console.WriteLine("Done...");
            // Console.WriteLine("Writing excel report...");
            // ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("MVA3", mvaStats);
            // Console.WriteLine("Done");

            var incrStats = new INCRMain().RunINCR(10, 0);
            Console.WriteLine("Done...");
            Console.WriteLine("Writing excel report...");
            ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook("INCR2", incrStats);
            Console.WriteLine("Done");
        }
    }
}
