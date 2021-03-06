#!/usr/bin/env python

import os
import sys
import glob
import random
from math import sqrt

import numpy as np

sys.path.insert(0, os.pardir)
from testing_harness import PyAPITestHarness
import openmc
import openmc.model


class TRISOTestHarness(PyAPITestHarness):
    def _build_inputs(self):
        # Define TRISO matrials
        fuel = openmc.Material()
        fuel.set_density('g/cm3', 10.5)
        fuel.add_nuclide('U-235', 0.14154)
        fuel.add_nuclide('U-238', 0.85846)
        fuel.add_nuclide('C-Nat', 0.5)
        fuel.add_nuclide('O-16', 1.5)

        porous_carbon = openmc.Material()
        porous_carbon.set_density('g/cm3', 1.0)
        porous_carbon.add_nuclide('C-Nat', 1.0)
        porous_carbon.add_s_alpha_beta('Graph', '71t')

        ipyc = openmc.Material()
        ipyc.set_density('g/cm3', 1.90)
        ipyc.add_nuclide('C-Nat', 1.0)
        ipyc.add_s_alpha_beta('Graph', '71t')

        sic = openmc.Material()
        sic.set_density('g/cm3', 3.20)
        sic.add_element('Si', 1.0)
        sic.add_nuclide('C-Nat', 1.0)

        opyc = openmc.Material()
        opyc.set_density('g/cm3', 1.87)
        opyc.add_nuclide('C-Nat', 1.0)
        opyc.add_s_alpha_beta('Graph', '71t')

        graphite = openmc.Material()
        graphite.set_density('g/cm3', 1.1995)
        graphite.add_nuclide('C-Nat', 1.0)
        graphite.add_s_alpha_beta('Graph', '71t')

        # Create TRISO particles
        spheres = [openmc.Sphere(R=r*1e-4)
                   for r in [212.5, 312.5, 347.5, 382.5]]
        c1 = openmc.Cell(fill=fuel, region=-spheres[0])
        c2 = openmc.Cell(fill=porous_carbon, region=+spheres[0] & -spheres[1])
        c3 = openmc.Cell(fill=ipyc, region=+spheres[1] & -spheres[2])
        c4 = openmc.Cell(fill=sic, region=+spheres[2] & -spheres[3])
        c5 = openmc.Cell(fill=opyc, region=+spheres[3])
        inner_univ = openmc.Universe(cells=[c1, c2, c3, c4, c5])

        outer_radius = 422.5*1e-4
        trisos = []
        random.seed(1)
        for i in range(100):
            # Randomly sample location
            lim = 0.5 - outer_radius*1.001
            x = random.uniform(-lim, lim)
            y = random.uniform(-lim, lim)
            z = random.uniform(-lim, lim)
            t = openmc.model.TRISO(outer_radius, inner_univ, (x, y, z))

            # Make sure TRISO doesn't overlap with another
            for tp in trisos:
                xp, yp, zp = tp.center
                distance = sqrt((x - xp)**2 + (y - yp)**2 + (z - zp)**2)
                if distance <= 2*outer_radius:
                    break
            else:
                trisos.append(t)

        # Define box to contain lattice
        min_x = openmc.XPlane(x0=-0.5, boundary_type='reflective')
        max_x = openmc.XPlane(x0=0.5, boundary_type='reflective')
        min_y = openmc.YPlane(y0=-0.5, boundary_type='reflective')
        max_y = openmc.YPlane(y0=0.5, boundary_type='reflective')
        min_z = openmc.ZPlane(z0=-0.5, boundary_type='reflective')
        max_z = openmc.ZPlane(z0=0.5, boundary_type='reflective')
        box = openmc.Cell(region=+min_x & -max_x & +min_y & -max_y & +min_z & -max_z)

        # Create lattice
        ll, ur = box.region.bounding_box
        shape = (3, 3, 3)
        pitch = (ur - ll) / shape
        lattice = openmc.model.create_triso_lattice(
            trisos, ll, pitch, shape, graphite)
        box.fill = lattice

        root = openmc.Universe(0, cells=[box])
        geom = openmc.Geometry(root)
        geom.export_to_xml()

        settings = openmc.Settings()
        settings.batches = 5
        settings.inactive = 0
        settings.particles = 100
        settings.source = openmc.Source(space=openmc.stats.Point())
        settings.export_to_xml()

        mats = openmc.Materials([fuel, porous_carbon, ipyc, sic, opyc, graphite])
        mats.default_xs = '71c'
        mats.export_to_xml()


if __name__ == '__main__':
    harness = TRISOTestHarness('statepoint.5.h5')
    harness.main()
